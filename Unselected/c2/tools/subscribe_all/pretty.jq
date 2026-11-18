.topic as $topic
| .payload
| if . == null or . == "" then
    $topic
  else
    (. as $raw | try fromjson catch $raw)
    | if type == "array" and length > 0 and (.[0] | type) == "array" then
        $topic, (.[] | tojson)
      elif type == "object" then
        ([keys_unsorted[] | select(startswith("cell_"))] | .[:-1] | map([.])) as $other_cells
        | $topic, delpaths($other_cells)
      else
        "\($topic) \(if type == "string" then . else tojson end)"
      end
  end
