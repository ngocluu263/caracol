module.exports = function(app, passport, auth) {

  /* -------------start of prefab MEAN routes-------------*/
    //User Routes
    // var users = require('../controllers/users');
    // app.get('/signin', users.signin);
    // app.get('/signup', users.signup);
    // app.get('/signout', users.signout);
  /* -------------end of prefab MEAN routes-------------*/

    //home rolled User routes
    //TODO: refactor to utilize MEAN routing & functions
    var async = require('async');
    var params;

    app.post('/signup', function(req, res){
      console.log('signup request looks like:', req.body);
      async.waterfall([
        function(callback) {
          dbClient.createUser(req.body.params, callback);
        }
      ], function(error, user) {
        console.log('data', user);
        if (error) {
          res.send(409, error);
        } else {
          console.log('sending up new user_id', user.id);
          req.session.auth = true;
          req.session.user_id = user.id;
          res.send(200, {
            id: user.id,
            username: user.username
          });
        }
      });
    });

    app.post('/login', function(req, res){
      console.log('login request looks like:', req.body);
      async.waterfall([
        function(callback) {
          dbClient.findUser(req.body.params, callback);
        }
      ], function(error, user){
        if (error) {
          res.send(500, error);
        } else {
          req.session.user_id = user.id;
          req.session.auth = true;
          res.send(200, {
            id: user.id,
            username: user.username
          });
        }
      });
    });

    app.post('/logout', function(req, res) {
      req.session = null;
      res.send('logged out');
    });

    //loads all dependencies and app for bookmarklet
    app.get('/bookmarklet/dependencies', function(req, res){
      async.eachSeries(
        ['./public/bower_components/underscore/underscore-min.js',
         './public/bower_components/angular-route/angular-route.min.js',
         './dist/bookmarklet/bookmarkletApp.js'],
        function(filename, cb) {
          console.log('well these are good');
          fs.readFile(filename, function(error, data) {
            if (!error) {
              res.write(data);
            }
            cb(error);
          });
        },
        function(error) {
          console.log('error loading bookmarklet dependencies', error);
          res.end();
        }
      );
    });

    //loads css for bookmarklet
    app.get('/dist/bookmarklet/caracol.css', function(req, res){
      fs.readFile('./dist/bookmarklet/caracol.css', function(error, data){
        if (error){
          console.log(error);
        } else {
          res.end(data);
        }
      });
    });

    app.get('/partials/login.html', function(req, res){
      fs.readFile('./dist/bookmarklet/partials/login.html', function(error, data){
        if (error){
          console.log(error);
        } else {
          res.end(data);
        }
      });
    });

    app.get('/partials/vote.html', function(req, res){
      fs.readFile('./dist/bookmarklet/partials/vote.html', function(error, data){
        if (error){
          console.log(error);
        } else {
          res.end(data);
        }
      });
    });

    app.get('/partials/recommendation.html', function(req, res){
      fs.readFile('./dist/bookmarklet/partials/recommendation.html', function(error, data){
        if (error){
          console.log(error);
        } else {
          res.end(data);
        }
      });
    });


  /* -------------start of prefab MEAN routes-------------*/
    //Setting up the users api
    // app.post('/users', users.create);

    // app.post('/users/session', passport.authenticate('local', {
    //     failureRedirect: '/signin',
    //     failureFlash: 'Invalid email or password.'
    // }), users.session);

    // app.get('/users/me', users.me);

    // //Finish with setting up the userId param
    // app.param('userId', users.user);

    // //Article Routes
    // var articles = require('../app/controllers/articles');
    // app.get('/articles', articles.all);
    // app.post('/articles', auth.requiresLogin, articles.create);
    // app.get('/articles/:articleId', articles.show);
    // app.put('/articles/:articleId', auth.requiresLogin, auth.article.hasAuthorization, articles.update);
    // app.del('/articles/:articleId', auth.requiresLogin, auth.article.hasAuthorization, articles.destroy);

    // //Finish with setting up the articleId param
    // app.param('articleId', articles.article);
  /* -------------end of prefab MEAN routes-------------*/

    //Inject script onto current page
    var fs = require('fs');
    app.get('/script', function(req, res){
      fs.readFile('./dist/bookmarklet/templates/home.html', function(error, data){
        if (error) {
        console.log(error);
        } else {
          res.end(data);
        }
      });
    });

    app.get('/app/:url/:t/*', function(req, res){
      console.log('requesting app');
        
      console.log('7');
        async.eachSeries(
        ['./public/bower_components/jquery/jquery.min.js', './dist/bookmarklet/script.js'],
        function(filename, cb) {
          fs.readFile(filename, function(error, data) {
            if (!error) {
              res.write(data);
            }
            cb(error);
          });
        },
        function(error) {
          if (error){
            console.log('error loading injection scripts', error);
          }
          res.end();
        }
      );
    });

    //CORS preflight path
    app.options('/*', function(req, res){
      res.header('Access-Control-Allow-Origin', '*');
      res.header('Access-Control-Allow-Headers', 'Content-Type');
      res.send(200, res.header);
    });

    var dbClient = require('../database/dbclient.js');
    var token = process.env.APPSETTING_readability_key || require(__dirname + '/config.js').token;
    var parser = require('../controllers/parser.js').parser;

    app.post('/uri', auth.hasAuthorization, function(req, res){
      params = {
        url: decodeURIComponent(req.body.uri),
        token: token
      };
      console.log('0')
      var user_id = req.session.user_id;
      res.header("Access-Control-Allow-Origin", "*");
      async.waterfall([
        function(callback){
          console.log('1')
          parser(params, callback);
        },
        function(response, callback){
          console.log('2')
          response.url = params.url;
          dbClient.checkForClipping(response, user_id, callback);
        },
        function(clipping_id, callback){
          console.log('3')
          clipping_id = clipping_id.toString();
          res.send(200, clipping_id);
          callback(null);
        }
      ], function(error) {
        console.log('4')
        if (error) {
          console.log('5')
          res.send(500, error);
        }
      });
    });

    app.post('/testcorpus', function(req, res) {
      params = {
        url: decodeURIComponent(req.body.uri),
        token: token
      };
      var user_id = 70; // this is the user_id for the testcorpus user
      res.header("Access-Control-Allow-Origin", "*");
      async.waterfall([
        function(callback){
          parser(params, callback);
        },
        function(response, callback){
          response.url = params.url;
          dbClient.dbInsert(response, user_id, callback);
        },
        function(clipping_id, callback){
          clipping_id = clipping_id.toString();
          console.log('clipping id before reply to client is:', clipping_id);
          res.send(200, clipping_id);
          callback(null);
        }
      ], function(error) {
        if (error) {
          res.send(500, error);
        }
      });
    });

    var handleFetching = function(clippings_or_recs, req, res) {
      // improve this checking
      if (parseInt(req.query.lastId) < 0 || !req.query.batchSize) {
        res.send(400, 'Poorly formed request');
      // should also add handling for when user is not authorized --> respond with 401
      } else {
        async.waterfall([
          function(callback) {
            dbClient.fetch(clippings_or_recs, req.session.user_id, parseInt(req.query.lastId), req.query.batchSize, callback);
          },
          function(clippings, callback) {
            console.log('about to send clippings back to client');
            res.send(clippings);
            callback(null);
          }
        ]);
      }
    };

    // route for loading user's clippings
    app.get('/fetchmyclippings', auth.hasAuthorization, function(req, res) {
      handleFetching('clippings', req, res);
    });

    // route for loading recommendations for a user
    app.get('/fetchmyrecommendations', auth.hasAuthorization, function(req, res) {
      handleFetching('recs', req, res);
    });

    // route for storing a vote from the user's clippings view
    app.post('/vote/:uri', auth.hasAuthorization, function(req, res) {
      //req.params.uri
      var params = {
        //TODO grab clipping_id from session with uri
        //clipping_id: req.params.clipping_id,
        vote: req.body.vote,
        //TODO grab user_id from session
      };
      res.end(dbClient.dbVote(params));
    });

    //Home route
    var index = require('../controllers/index');
    app.get('/', index.render);

};
