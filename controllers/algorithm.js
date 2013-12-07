var zerorpc = require("zerorpc");
var pyserver =  require("../config/python.json");

var client = new zerorpc.Client();
client.connect("tcp://" + pyserver.host + ":" + pyserver.port);

exports.removeHTMLAndTokenize = removeHTMLAndTokenize = function(clippingId, callback) {
  client.invoke("remove_html_and_tokenize_clipping_content", clippingId, function(error, res, more) {
    console.log(res);
    callback(error, res);
  });
};

// tokenizedClippings = [];
// first_tokenized = 107 ;
// last_tokenized =  165 ;
// for(clippingId = first_tokenized; clippingId <= last_tokenized; clippingId++){
//   tokenizedClippings.push(removeHTMLAndTokenize(clippingId));
// }; 

// console.log(tokenizedClippings);