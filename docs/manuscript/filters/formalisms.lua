function Pandoc(document)
  if FORMAT:match('latex') and PANDOC_VERSION < pandoc.types.Version('3.10.1') then
    error('PDF table placement requires Pandoc >= 3.10.1')
  end
  local numbers = {}
  local counter = 0
  local figures = {}
  local figure_counter = 0
  document = document:walk({
    Math = function(math)
      if math.mathtype ~= 'DisplayMath' then return math end
      local label = math.text:match('\\label{(eq:[%w_%-]+)}')
      if not label then error('Every display formalism requires a named eq: label') end
      if math.text:match('\\tag') or math.text:match('\\eqno') or math.text:match('\\leqno') then
        error('Display formalism numbers must be generated, not authored')
      end
      if numbers[label] then error('Duplicate formalism label: ' .. label) end
      counter = counter + 1
      numbers[label] = counter
      local expression, label_count = math.text:gsub('\\label{eq:[%w_%-]+}', '')
      if label_count ~= 1 then error('Every display formalism requires exactly one label') end
      expression = expression:match('^%s*(.-)%s*$')
      if FORMAT:match('latex') then
        return pandoc.RawInline('latex', '\\begin{equation}\n' .. expression ..
          '\n\\label{' .. label .. '}\\end{equation}')
      end
      return pandoc.Span({pandoc.Math('DisplayMath', expression),
        pandoc.Span({pandoc.Str('(' .. counter .. ')')}, pandoc.Attr('', {'equation-number'}))},
        pandoc.Attr(label, {'formalism'}, {['data-equation-number'] = tostring(counter)}))
    end,
    Figure = function(figure)
      local label = figure.identifier
      if not label:match('^fig%-[%w_%-]+$') then error('Every figure requires a fig- identifier') end
      if figures[label] then error('Duplicate figure label: ' .. label) end
      if pandoc.utils.stringify(figure.caption.long):match('^Figure%s+%d+') then
        error('Figure numbers must be generated, not authored')
      end
      figure_counter = figure_counter + 1
      figures[label] = figure_counter
      figure.attributes['data-figure-number'] = tostring(figure_counter)
      if FORMAT:match('latex') and document.meta['publication-figure-width'] then
        figure = figure:walk({
          Image = function(image)
            image.attributes.width = pandoc.utils.stringify(document.meta['publication-figure-width'])
            -- Leave room for the caption and footer on a full-page portrait view.
            image.attributes.height = '83%'
            return image
          end
        })
      end
      if FORMAT:match('html') then
        local caption = figure.caption.long[1]
        if not caption or (caption.t ~= 'Plain' and caption.t ~= 'Para') then
          error('Figure requires a text caption')
        end
        caption.content:insert(1, pandoc.Strong({pandoc.Str('Figure ' .. figure_counter .. '.')}))
        caption.content:insert(2, pandoc.Space())
      end
      return figure
    end
  })
  document = document:walk({
    Link = function(link)
      local label = link.target:match('^#(eq:[%w_%-]+)$')
      local figure = link.target:match('^#(fig%-[%w_%-]+)$')
      if label then
        if not numbers[label] then error('Unknown formalism reference: ' .. label) end
        link.content = {pandoc.Str('Equation (' .. numbers[label] .. ')')}
      elseif figure then
        if not figures[figure] then error('Unknown figure reference: ' .. figure) end
        link.content = {pandoc.Str('Figure ' .. figures[figure])}
      end
      if FORMAT:match('latex') and link.target:match('^#ref%-') then
        local context = pandoc.Cite({link}, {})
        local citation = pandoc.write(pandoc.Pandoc({pandoc.Plain({context})}), 'latex')
        citation = citation:gsub('%s+$', '')
        -- Keep short author-year labels together, but let long labels fit body or table measures.
        return pandoc.RawInline('latex',
          '{\\sbox0{' .. citation .. '}\\ifdim\\wd0>\\dimexpr\\linewidth/3\\relax '
          .. citation .. '\\else\\usebox0\\fi}')
      end
      return link
    end
  })
  return document:walk({
    Table = function(tabular)
      if not FORMAT:match('latex') then return tabular end
      local rows = #tabular.head.rows + #tabular.foot.rows
      for _, body in ipairs(tabular.bodies) do
        rows = rows + #body.head + #body.body
      end
      -- Keep compact summaries whole; full interval and settings tables still paginate.
      if rows > 12 or #pandoc.utils.stringify(tabular) > 1600 then return tabular end
      tabular.classes:insert('float')
      tabular.attributes['latex-placement'] = 'H'
      return {pandoc.RawBlock('latex', '\\par\\penalty0'), tabular}
    end
  })
end
