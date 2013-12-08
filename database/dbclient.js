//dbclient.js

var tables = require('./dbschemas.js');
var algorithm = require('../controllers/algorithm.js');
var _ = require('underscore');
var crypto = require('crypto');

// convert a datetime in ISO format generated by Javascript's Date object into Postgres format
var dateTransform = function(ISOdatetime) {
  ISOdatetime = ISOdatetime.replace('T',' ');
  ISOdatetime = ISOdatetime.slice(0,19);
  ISOdatetime = ISOdatetime + '+00';
  return ISOdatetime;
};

var insertUserClipping = function(user_id, clipping_id, callback){
  new tables.User_Clipping({
    user_id: user_id,
    clipping_id: clipping_id
  })
  .save()
  .then(function(model){
    console.log('success to the user clipping table:', model.attributes);
    callback(null, model.attributes.clipping_id);
  }, function(error){
    console.log('error adding to user_clippings', error);
  });
};

var makeSalt = function() {
  return Math.round((new Date().valueOf() * Math.random())) + '';
};
  
var encryptPassword = function(password, salt){
  if (!password) { return ''; }
  salt = salt || makeSalt();
  var hashed_password = crypto.createHmac('sha1', salt).update(password).digest('hex');
  return {
    password_salt: salt,
    hashed_password: hashed_password
  };
};

exports.createUser = createUser = function(json, callback){
  console.log('json looks like:', json);
  var creds = encryptPassword(json.password);
  var lowerUsername = json.username.toLocaleLowerCase();
  new tables.User()
  .query(function(qb) {
    qb.where({username: lowerUsername})
  })
  .fetch({require: true})
  .then(function(model){
    console.log('results of username lookup:', model);
    callback('username already exists');
  }, function(err){
    console.log("no user by that username found, so we'll create one");
    new tables.User({
      username: lowerUsername,
      password_salt: creds.password_salt,
      hashed_password: creds.hashed_password
    })
    .save()
    .then(function(model){
      console.log('model after saving:', model);
      console.log('user successfully saved:', model.id);
      callback(null, model.id);
    }, function(error){
      console.log('error creating new user:', error);
      callback(error);
    });
  });
};

exports.findUser = findUser = function(json, callback){
  var user = new tables.User({
    username: json.username.toLocaleLowerCase(),
  })
  .fetch({require: true})
  .then(function(model) {
    console.log('found user');
    var creds = encryptPassword(json.password, model.passwordSALT);
    if (model.hashed_password === creds.hashed_password) {
      callback(null, model.id);
    } else {
      callback('incorrect password');
    }
  }, function(error){
    console.log('please signup!', error);
    callback(error);
  });
};

exports.dbInsert = dbInsert = function(json, user_id, callback){
  //TODO prevent duplicate clippings by
  //periodically scanning for duplictes in database

  //check: clipping already exists?

  //if so, capture that clipping id
  //if not, return the new clipping id

  new tables.Clipping({
    title: json.title,
    content: json.content,
    uri: json.url,
    word_count: json.word_count,
    first_insert: dateTransform(new Date().toISOString()),
    total_pages: json.total_pages,
    date_published: json.date_published,
    dek: json.dek,
    lead_image_url: json.lead_image_url,
    next_page_id: json.next_page_id,
    rendered_pages: json.rendered_pages
  })
  .save()
  .then(function(model) {
    console.log('HAHHHAAA', model.id, user_id);
    console.log('finished saving the clipping');
    console.log('model.id is:', model.id);
    insertUserClipping(user_id, model.id, callback);
    algorithm.removeHTMLAndTokenize(model.id, function(){});
  }, function(error){
    console.log('Error saving the clipping');
    callback(error);
  });
};

exports.fetch = fetch = function(clippings_or_recs, user_id, fetchOlderThanThisId, batchSize, callback) {
  console.log('fetchClippingsOlderThanThisClippingId:',fetchOlderThanThisId);
  console.log('batchSize is:', batchSize);
  var coll, compar;
  if (clippings_or_recs === 'clippings') {
      compar = function(model) {
      return -1 * model.id; // sort so that most recent clippings displayed first
    };
    coll = new tables.User_Clippings({ comparator: compar });
  } else if (clippings_or_recs === 'recs') {
    compar = 'rank';
    coll = new tables.Recommendations({ comparator: compar });
  }

  var queryBuilder;
  if (fetchOlderThanThisId === 0) {
    queryBuilder = function(qb) {
      qb
      .orderBy('id', 'desc')
      .limit(batchSize);
      // once user_id is working, add .where('user_id', '=', '*').andWhere
    };
  } else {
    queryBuilder = function(qb) {
      qb
      .where('id', '<', fetchOlderThanThisId)
      .orderBy('id', 'desc')
      .limit(batchSize);
      // once user_id is working, add .where('user_id', '=', '*').andWhere
    };
  }
  coll.query(queryBuilder)
  .fetch({ withRelated: ['clipping'] })
  .then(function(results) {
    console.log('successfully grabbed', clippings_or_recs, 'from the db:', results);
    callback(null, results);
  }, function(error) {
    console.log('there was an error fetching', clippings_or_recs, 'from the db:', error);
    callback(error);
  });
  // once user_id is working, add .query(function(qb){qb.where('user_id', '=', user_id)})
};

exports.dbVote = dbVote = function(json){
  //update query update user clippings set vote where user clipping ==
  console.log('called', json);
  new tables.User_Clipping()
  .query()
  .where({user_id: json.user_id, clipping_id: json.clipping_id})
  .then(function(model){
    console.log(model[0].id);
    new tables.User_Clipping({id: model[0].id})
    .save({vote: json.vote}).then(function(model){
      console.log('look what i did ma', model);
    }, function(){
      console.log('error saving to userclipping id');
    });
  }, function(){
    console.log('welcome ot the danger zone');
  });
};
