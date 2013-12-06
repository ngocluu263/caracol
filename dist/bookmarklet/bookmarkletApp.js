//angular app

var app = angular.module('app', ['angularLocalStorage',
                                 'app.controllers',
                                 'app.services',
                                 'app.directives'
                                 ]);

app.run(function($q, $http, $rootScope, UploadService,storage){
  var url = (window.location !== window.parent.location) ? document.referrer: document.location;
  var uri = encodeURIComponent(url);
  var user_id = storage.get('caracolID');

  UploadService.sendToURI(uri, user_id)
  .then(function(data){
    
    //this grabs the bookmarklets parent url
    var url = (window.location !== window.parent.location) ? document.referrer: document.location;
    
    //sets up local storage clippings id
    //TODO: change to object {'clippings': {user_id.toString(): {url: url, clipping_id: Number(data)}}}
    if (!storage.get('clippings'+user_id)){
      storage.set('clippings'+user_id, [{url: url, clipping_id: Number(data)}]);
    } else {
      var clippingsArr = storage.get('clippings'+user_id);
      
      clippingsArr.push({url: url, clipping_id: Number(data)});
      storage.set('clippings'+user_id, clippingsArr);
    }
    console.log('clipping ids from storage', storage.get('clippings'+user_id));
  });
});

var services = angular.module('app.services', []);

services.factory('UploadService', function($q, $http){
  var service = {
    sendToURI: function(uri, user_id){
      console.log(uri);
      var d = $q.defer();
      $http.post('/uri', {
        uri: uri,
        user_id: user_id
      }).success(function(data){
        d.resolve(data);
      }).error(function(data){
        d.reject(data);
        console.log('error parsing article', data);
      });
      return d.promise;
    }
  };
  return service;
});

services.factory('VoteService', function($q, $http) {
  var service = {
    vote: function(user_id, vote, clipping_id){
      var d = $q.defer();
      $http.post('/vote/'+clipping_id, {
        vote: vote,
        user_id: user_id,
        clipping_id: clipping_id
      }).success(function(data){
        d.resolve(data);
      }).error(function(data){
        console.log('posting error', data);
        d.reject(data);
      });
      return d.promise;
    }
  };
  return service;
});

var controllers = angular.module('app.controllers', []);

controllers.controller('VoteCtrl', function($scope, VoteService, storage){
  $scope.voted = false;

  $scope.log = function(vote){
    !!vote ? ($scope.like = true) : ($scope.dislike = true);
  };

  $scope.vote = function(vote){
    //grabs uri and vote status
    var clipping_id;
    var url = (window.location !== window.parent.location) ? document.referrer: document.location;
    var user_id = storage.get('caracolID');
    var clippings = storage.get('clippings' + user_id);
    for (var i=0; i<clippings.length; i++){
      if (clippings[i].url === url){
        clipping_id = clippings[i].clipping_id;
        console.log(clipping_id);
      }
    }

    VoteService.vote(user_id, vote, clipping_id);
    $scope.log(vote);
    $scope.voted = true;
  };
  $scope.revert = function(preference){
    $scope.voted = false;
    $scope[preference] = false;
  };
});

var directives = angular.module('app.directives', []);

directives.directive('ngHome', function() {
  return {
    restrict: 'A',
    require: '^ngModel',
    templateUrl: 'dist/bookmarklet/templates/home.html'
  };
});