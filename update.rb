require "nokogiri"
require "json"

ja_doc = File.open("src/lagos_ja.ts") { |f| Nokogiri::XML(f) }
zh_doc = File.open("src/lagos_zh.ts") { |f| Nokogiri::XML(f, &:noblanks) }

extract_structure = ->(doc) {
  doc.xpath("//context").map do |context|
    res = []
    context_name = context.xpath("name").text
    res << context_name
    res << context.xpath("message").map do |message|
      message.xpath("source").text
    end.sort
    res
  end.sort_by { |x| x[0] }
}

ja = extract_structure.call(ja_doc)
zh = extract_structure.call(zh_doc)

# debug & log
# File.write("src/lagos_ja.json", ja.to_json)
# File.write("src/lagos_zh.json", zh.to_json)

# diff structure ja - zh
ja_hash = ja.to_h
zh_hash = zh.to_h
ja_hash.each do |k, v|
  unless zh_hash[k].nil?
    ja_hash[k] = v - zh_hash[k]
  end
end

# delete key with empty value
diff_nodes = ja_hash.delete_if { |_k, v| v.empty? }

diff_nodes.each do |name, messages|
  # find context by name with key
  context = zh_doc.xpath("//context[name='#{name}']").first
  # if context not exist, create new context
  if context.nil?
    context = Nokogiri::XML::Node.new("context", zh_doc)
    zh_doc.root.add_child(context)
    context.add_child(Nokogiri::XML::Node.new("name", zh_doc))
    context.xpath("name").first.content = name
  end
  # add message to context
  messages.each do |message|
    message_node = Nokogiri::XML::Node.new("message", zh_doc)
    message_node.add_child(Nokogiri::XML::Node.new("source", zh_doc))
    message_node.xpath("source").first.content = message
    # add emtpy translation node
    message_node.add_child('<translation type="unfinished"></translation>')
    context.add_child(message_node)
  end
end

# save to new file
zh_doc.write_xml_to(
  File.open("src/lagos_zh.ts", "wb"),
  indent: 4,
  save_with: Nokogiri::XML::Node::SaveOptions::NO_EMPTY_TAGS | Nokogiri::XML::Node::SaveOptions::FORMAT
)

# remove 4 space indent for every line between tag TS
File.write("src/lagos_zh.ts", File.read("src/lagos_zh.ts").gsub(/\n {4}/, "\n"))

# binding.irb
