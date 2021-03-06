services.factory('FetchService', ['$q', '$http', function($q, $http) {
  var service = {
    fetch: function(clippings_or_recs, lastId, batchSize) {
      console.log('lastId is:', lastId);
      var route, d = $q.defer();

      if (clippings_or_recs === 'clippings') {
        route = '/fetchMyClippings';
      } else if (clippings_or_recs === 'recs') {
        route = '/fetchMyRecommendations';
      }

      $http.get(route, {
        params: {
          lastId: lastId,
          batchSize: batchSize
        }
      }, {
        withCredentials: true
      })
      .success(function(data) {
        console.log('success fetching', ':', data);
        d.resolve(service.massage(data));
      })
      .error(function(reason) {
        console.log('error getting old:', reason);
        d.reject(reason);
      });
      return d.promise;
    },

    massage: function(data) {
      for (var i = 0; i < data.length; i++) {
        data[i].content_sans_html = data[i].clipping.content_sans_html || '';
        data[i].displayedExcerpt = data[i].content_sans_html.slice(0,250) + ' ...';
        data[i].elegantDate = service.elegantizeTimestamp(data[i]);
      }
      return data;
    },

    elegantizeTimestamp: function(article) {
      var numMilliseconds = new Date().getTime() - Date.parse(article.clipping.first_insert);
      var numSeconds = numMilliseconds/1000;
      var numMinutes = numSeconds/60;
      var numHours = numMinutes/60;
      if (numHours >= 24) {
        var month = article.clipping.first_insert.slice(5,7);
        var day = article.clipping.first_insert.slice(8,10);
        if (day[0] === '0') {
          day = day[1];
        }
        switch (month) {
          case '01':
            month = 'Jan';
            break;
          case '02':
            month = 'Feb';
            break;
          case '03':
            month = 'Mar';
            break;
          case '04':
            month = 'Apr';
            break;
          case '05':
            month = 'May';
            break;
          case '06':
            month = 'Jun';
            break;
          case '07':
            month = 'Jul';
            break;
          case '08':
            month = 'Aug';
            break;
          case '09':
            month = 'Sep';
            break;
          case '10':
            month = 'Oct';
            break;
          case '11':
            month = 'Nov';
            break;
          case '12':
            month = 'Dec';
            break;
        }
        return month + ' ' + day;
      } else {
        return 'today';
      }
    }
  };

  return service;
}]);