-- Pandoc filter for Google-Docs- and Word-exported reports (used after docx_mark_code.py)
-- * merges consecutive code paragraphs into one code block, unwraps
--   block quotes that only contain code (Google Docs indents code)
-- * guesses a language for JSON blocks
-- * removes bold/underline wrappers from headings and links

local function all_code(blocks)
  if #blocks == 0 then return false end
  for _, b in ipairs(blocks) do
    if b.t ~= "CodeBlock" then return false end
  end
  return true
end

local function merge(blocks)
  local out = pandoc.List()
  for _, b in ipairs(blocks) do
    if b.t == "BlockQuote" and all_code(b.content) then
      for _, c in ipairs(b.content) do
        c.text = c.text:gsub("^    ", "")
        out:insert(c)
      end
    else
      out:insert(b)
    end
  end
  local res = pandoc.List()
  for _, b in ipairs(out) do
    local prev = res[#res]
    if b.t == "CodeBlock" and prev and prev.t == "CodeBlock" then
      prev.text = prev.text .. "\n" .. b.text
    else
      res:insert(b)
    end
  end
  for _, b in ipairs(res) do
    if b.t == "CodeBlock" and #b.classes == 0 then
      -- strip common leading indentation
      local min
      for line in (b.text .. "\n"):gmatch("(.-)\n") do
        if line:match("%S") then
          local ind = #line:match("^ *")
          if not min or ind < min then min = ind end
        end
      end
      -- Word code paragraphs: "<indent>\t<more spaces>text" -> keep the indent before the tab
      b.text = b.text:gsub("\n( *)\t *", "\n%1"):gsub("^( *)\t *", "%1")
      if min and min > 0 then
        local lines = {}
        for line in (b.text .. "\n"):gmatch("(.-)\n") do
          table.insert(lines, line:sub(min + 1))
        end
        b.text = table.concat(lines, "\n")
      end
      local first = b.text:match("^%s*(%S)")
      if first == "{" or first == "[" then b.classes = {"json"} end
    end
  end
  return res
end

function Blocks(blocks)
  return merge(blocks)
end

-- Google Docs highlight marks (leftover review highlights): keep text only
function Span(s)
  if s.classes:includes("mark") then return s.content end
end

local function strip_inlines(inls)
  local res = pandoc.List()
  for _, i in ipairs(inls) do
    if i.t == "Strong" or i.t == "Underline" then
      res:extend(strip_inlines(i.content))
    else
      res:insert(i)
    end
  end
  return res
end

function Header(h)
  h.content = strip_inlines(h.content)
  return h
end

function Link(l)
  l.content = strip_inlines(l.content)
  return l
end

-- Word bookmarks (empty anchor spans, e.g. _Toc...): drop
local span_mark = Span
function Span(s)
  if s.classes:includes("anchor") and #s.content == 0 then return {} end
  return span_mark(s)
end

-- merge adjacent inline code (Word splits monospace runs)
function Inlines(inls)
  local res = pandoc.List()
  for _, i in ipairs(inls) do
    local prev = res[#res]
    if i.t == "Code" and prev and prev.t == "Code" then
      prev.text = prev.text .. i.text
    else
      res:insert(i)
    end
  end
  return res
end

-- Section labels and internal links.
-- Every heading gets a MyST label "<prefix>-<section number>" (dots -> dashes;
-- e.g. "clsinfra-d71-5-3-3-2"),
-- unnumbered headings "<prefix>-<pandoc identifier>". Internal links are
-- resolved by the section number in their text ("section 5.3.3.2"), since the
-- Google Docs bookmark ids they point to are not in the document; else by
-- heading identifier; unresolvable links are unlinked.
local function heading_label(prefix, h)
  local txt = pandoc.utils.stringify(h.content)
  local num = txt:match("^(%d+[%.%d]*)")
  if num then
    num = num:gsub("%.$", "")
    return prefix .. "-" .. num:gsub("%.", "-"), num
  end
  return prefix .. "-" .. h.identifier, nil
end

function Pandoc(doc)
  local prefix = doc.meta.rtfr_prefix and pandoc.utils.stringify(doc.meta.rtfr_prefix)
  if not prefix then return doc end
  -- label prefix: "d7-1" -> "clsinfra-d71" (project + deliverable; the hyphen
  -- after the deliverable number starts the section number)
  prefix = "clsinfra-" .. prefix:gsub("-", "")
  local bynum, byid = {}, {}
  for _, b in ipairs(doc.blocks) do
    if b.t == "Header" then
      local lab, num = heading_label(prefix, b)
      if num then bynum[num] = lab end
      byid[b.identifier] = lab
    end
  end
  doc = doc:walk({
    Link = function(l)
      -- internal: "#id", or Word bookmark links without a scheme ("Relations#_5.6.3.2_Tab_")
      if l.target:match("^%a[%w+.-]*:") or not l.target:find("#", 1, true) then return nil end
      local txt = pandoc.utils.stringify(l.content)
      local num = txt:match("(%d+[%.%d]*%d)") or txt:match("(%d+)")
      local lab = (num and bynum[num]) or byid[l.target:match("#(.*)$")]
      if lab then l.target = "#" .. lab; return l end
      io.stderr:write("unresolved internal link: " .. txt .. " -> " .. l.target .. "\n")
      return l.content
    end,
  })
  local out = pandoc.List()
  for _, b in ipairs(doc.blocks) do
    if b.t == "Header" and pandoc.utils.stringify(b.content):match("%S") then
      out:insert(pandoc.RawBlock("markdown", "(" .. heading_label(prefix, b) .. ")="))
    end
    out:insert(b)
  end
  doc.blocks = out
  return doc
end

-- Tables containing footnotes: MyST does not parse footnote references inside
-- HTML tables, and pandoc writes tables with merged cells as HTML. So such
-- tables are unmerged (content stays in the first cell of a span, the others
-- are left empty) and the first row becomes the header -> pipe table.
local function has_note(t)
  local found = false
  t:walk({ Note = function() found = true end })
  return found
end

local function unmerge_rows(rows, ncols)
  local pending = {}  -- pending[r][c] = true: slot filled by an earlier rowspan
  local out = pandoc.List()
  for r, row in ipairs(rows) do
    local cells, c = pandoc.List(), 1
    local placed = {}
    local function fill_pending()
      while pending[r] and pending[r][c] do
        cells:insert(pandoc.Cell({}))
        c = c + 1
      end
    end
    for _, cell in ipairs(row.cells) do
      fill_pending()
      local rs, cs = cell.row_span, cell.col_span
      cell.row_span, cell.col_span = 1, 1
      cells:insert(cell)
      for k = 1, cs - 1 do cells:insert(pandoc.Cell({})) end
      for rr = r + 1, r + rs - 1 do
        pending[rr] = pending[rr] or {}
        for k = 0, cs - 1 do pending[rr][c + k] = true end
      end
      c = c + cs
    end
    fill_pending()
    while #cells < ncols do cells:insert(pandoc.Cell({})) end
    row.cells = cells
    out:insert(row)
  end
  return out
end

function Table(t)
  if not has_note(t) then return nil end
  local ncols = #t.colspecs
  t.head.rows = unmerge_rows(t.head.rows, ncols)
  for _, b in ipairs(t.bodies) do
    b.body = unmerge_rows(b.body, ncols)
  end
  if #t.head.rows == 0 and #t.bodies > 0 and #t.bodies[1].body > 0 then
    t.head.rows = pandoc.List({ t.bodies[1].body:remove(1) })
  end
  for i, cs in ipairs(t.colspecs) do t.colspecs[i] = { cs[1], nil } end
  return t
end
