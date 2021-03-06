var Bookshelf  = require('bookshelf');
var credentials = require('./dbconfig.json');

module.exports.caracolPG = Bookshelf.initialize({
  client: 'pg',
  connection: {
    host     : credentials.host,    // when deploying use 'credentials.localhost' here
    user     : credentials.user,
    password : credentials.password,
    database : credentials.database,
    charset  : 'utf8'
  }
});
