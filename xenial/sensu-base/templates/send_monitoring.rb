#!/opt/sensu/embedded/bin/ruby
require 'sensu-handler'
require 'net/http'
require 'json'

class Show < Sensu::Handler
  def handle
    uri = URI('http://{{sojobo}}/monitoring')
    http = Net::HTTP.new(uri.host, uri.port)
    req = Net::HTTP::Post.new(uri.path, 'Content-Type' => 'application/json')
    req.basic_auth("{{user}}", "{{password}}")
    req.body = @event.to_json
    res = http.request(req)
  end
end
