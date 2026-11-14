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

-- highlights: kept as <span class="mark">; tools/highlights.py keeps only the
-- ones visible in the published PDF (alignment/<id>.highlights.json) and
-- removes leftover review highlights
function Span(s)
  if s.classes:includes("mark") then
    if not pandoc.utils.stringify(s.content):match("%S") then return s.content end
    -- keep the inner formatting (bold, italics, code)
    local out = pandoc.List({ pandoc.RawInline("html", '<span class="mark">') })
    out:extend(s.content)
    out:insert(pandoc.RawInline("html", "</span>"))
    return out
  end
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

-- links: drop the underline Google Docs adds, but keep bold (D7.4 marks the
-- changed parts of example URLs in bold)
local function strip_underline(inls)
  local res = pandoc.List()
  for _, i in ipairs(inls) do
    if i.t == "Underline" then
      res:extend(strip_underline(i.content))
    else
      res:insert(i)
    end
  end
  return res
end

function Link(l)
  l.content = strip_underline(l.content)
  return l
end

-- Word bookmarks (empty anchor spans, e.g. _Toc...): drop
local span_mark = Span
function Span(s)
  if s.classes:includes("anchor") and #s.content == 0 then return {} end
  return span_mark(s)
end

-- merge adjacent inline code (Word splits monospace runs); bold code was
-- marked with U+2063 by docx_mark_code.py and becomes Strong(Code)
local BOLD = "\u{2063}"
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
  for k, i in ipairs(res) do
    if i.t == "Code" and i.text:find(BOLD, 1, true) then
      local bold = i.text:sub(1, #BOLD) == BOLD and i.text:sub(-#BOLD) == BOLD
      i.text = i.text:gsub(BOLD, "")
      if bold then res[k] = pandoc.Strong({ i }) end
    elseif i.t == "Str" and i.text:find(BOLD, 1, true) then
      i.text = i.text:gsub(BOLD, "")
    end
  end
  -- adjacent bold pieces (e.g. bold text + bold code) -> one Strong
  local merged = pandoc.List()
  for _, i in ipairs(res) do
    local prev = merged[#merged]
    if i.t == "Strong" and prev and prev.t == "Strong" then
      prev.content:extend(i.content)
    else
      merged:insert(i)
    end
  end
  return merged
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
  -- unnumbered: short, readable id (MyST ignores labels over ~100 characters,
  -- and paragraph labels add "-pNN"): text before a colon, at most 50 chars
  local ident = h.identifier
  local short = txt:match("^([^:]+):")
  if short or #ident > 50 then
    ident = (short or txt):lower():gsub("[^a-z0-9]+", "-"):gsub("^-+", ""):gsub("-+$", "")
    if #ident > 50 then ident = ident:sub(1, 50):gsub("-[^-]*$", "") end
  end
  -- same normalisation as MyST applies to ids: [a-z0-9-] only
  ident = ident:lower():gsub("[^a-z0-9]+", "-"):gsub("^-+", ""):gsub("-+$", "")
  return prefix .. "-" .. ident, nil
end

function Pandoc(doc)
  local prefix = doc.meta.rtfr_prefix and pandoc.utils.stringify(doc.meta.rtfr_prefix)
  if not prefix then return doc end
  -- the prefix is the report id, e.g. "clsinfra-d71" (project + deliverable)
  local bynum, byid, used, labels = {}, {}, {}, {}
  for i, b in ipairs(doc.blocks) do
    if b.t == "Header" and pandoc.utils.stringify(b.content):match("%S") then
      local lab, num = heading_label(prefix, b)
      if used[lab] then  -- e.g. two sections with the same title
        local k = 2
        while used[lab .. "-" .. k] do k = k + 1 end
        lab = lab .. "-" .. k
      end
      used[lab] = true
      labels[i] = lab
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
  for i, b in ipairs(doc.blocks) do
    if labels[i] then
      out:insert(pandoc.RawBlock("markdown", "(" .. labels[i] .. ")="))
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
      -- paragraphs in a cell -> one plain text (pipe tables need Plain);
      -- several paragraphs are joined with a space
      local all_text = #cell.contents > 0
      for _, blk in ipairs(cell.contents) do
        if blk.t ~= "Para" and blk.t ~= "Plain" then all_text = false end
      end
      if all_text then
        local inl = pandoc.List()
        for n, blk in ipairs(cell.contents) do
          if n > 1 then inl:insert(pandoc.Space()) end
          inl:extend(blk.content)
        end
        cell.contents = { pandoc.Plain(inl) }
      end
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
