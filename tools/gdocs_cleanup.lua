-- Pandoc filter for Google-Docs-exported reports (used after docx_mark_code.py)
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
