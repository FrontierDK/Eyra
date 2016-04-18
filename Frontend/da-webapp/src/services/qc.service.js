(function () {
// service to handle all processing realted to the QC. Querying the server, processing the information for example.

'use strict';

angular.module('daApp')
  .factory('qcService', qcService);

qcService.$inject = ['$q', 'dataService', 'deliveryService', 'logger', 'utilityService'];

function qcService($q, dataService, deliveryService, logger, utilityService) {
  var qcHandler = {};
  var delService = deliveryService;
  var util = utilityService;

  qcHandler.notifySend = notifySend;

  // counter for the total times recording.controller.js 
  // has notified us of a send during this session
  var totalNotifies = 0;
  // counter to use for QC, counts how many recordings have been sent,
  //   since last reset of counter.
  var modSendCounter = 0;

  return qcHandler;

  //////////


  function notifySend(sessionId, tokenCount) {
    // tokenCount is the total count of token reads by current speaker
    // if tokenCount === 0 it is a new speaker
    totalNotifies++;
    modSendCounter++;
    //console.info(totalNotifies + ' totalNotifies'); 

    // if totalNotifies is higher than the token count, it probably means
    //   a new user is recording starting at 0 tokens read.
    if (totalNotifies > tokenCount) {
      totalNotifies = 1;
      modSendCounter = 1;
    }

    if (modSendCounter >= (util.getConstant('QCFrequency' || 5))
       && totalNotifies >= (util.getConstant('QCInitRecThreshold') || 10)) {
      modSendCounter = 0;

      return delService.queryQC(sessionId)
      .then(handleQCReport, util.stdErrCallback);

    } else {
      
      return $q.reject(false);
    }
  }

  function calcAvgAcc(report) {
    /*
      Calculates weighted (right now equally) accuracy of all the modules
      from the QC report.

      parameters:
        report  the QC report as described in client server api.
      return: 
        a in [0.0 .. 1.0]
    */
    var acc = 0;
    var cnt = 0;
    for (var mod in report.modules) {
      if (!report.modules.hasOwnProperty(mod)) continue;

      var module = report.modules[mod];
      acc += module.totalStats.accuracy;
      cnt++;
    }
    return acc/cnt;
  }

  function handleQCReport(response) {
    var report = response.data;

    // calulate average accuracy of all QC modules
    var avgAcc = calcAvgAcc(report);
    report.avgAcc = avgAcc;

    var tokenAnnouncement = handleTokenAnnouncements(report);

    // displayReport is in HTML
    var displayReport = prettify(report);
    dataService.set('QCReport', displayReport);

    // message to send back to recording.controller.js notifying that we wish
    //   results to be displayed.
    var displayResults = tokenAnnouncement
                         || avgAcc < util.getConstant('QCAccThreshold');
    if (displayResults) {
      return $q.when(true);
    } else {
      return $q.reject(false);
    }
  }

  // like for example, display, good job! on each 50 tokens read.
  // adds key tokenCount and tokenCountMsg to report.
  function handleTokenAnnouncements(report) {
    var tokensRead = dataService.get('speakerInfo').tokensRead;
    
    // for tokenAnnouncement to be true modulus of tokenAnnouncement 
    // and TokenAnnouncementFrequency need to be 0
    var tokenAnnouncement = totalNotifies > 0
                            && totalNotifies % util.getConstant('TokenAnnouncementFreq') === 0;

    var totalTokens = util.getConstant('TokenCountGoal') || 260;
    if (tokenAnnouncement) {
      var _totalNotifies;
      if (tokensRead){
        _totalNotifies = tokensRead;
      } else {
        _totalNotifies = totalNotifies;
      }

      report.tokenCount =  tokensRead;
      // some gamifying messages to pump up the speakers
      report.tokenCountMsg = 'Nice, '+util.percentage(_totalNotifies, totalTokens, 2)+'% of the tokens read, keep going.';
      if (totalNotifies >= 100 && totalNotifies < 200) {
        report.tokenCountMsg = 'Sweet, '+util.percentage(_totalNotifies, totalTokens, 2)+'% of the tokens.';
      }
      if (totalNotifies >= 200 && totalNotifies < 300) {
        report.tokenCountMsg = util.percentage(_totalNotifies, totalTokens, 2)+'% of the tokens? Wow.'
      }
      if (totalNotifies >= 300 && totalNotifies < 400) {
        report.tokenCountMsg = 'Awesome, '+util.percentage(t_otalNotifies, totalTokens, 2)+'% of the tokens. Just awesome';
      }
      if (totalNotifies >= 400) {
        report.tokenCountMsg = 'You are a god: '+util.percentage(_totalNotifies, totalTokens, 2)+'% of the tokens.';
      }

      var tokensLeftToRead = totalTokens - tokensRead;

      if (tokensLeftToRead > 0){
        report.tokensLeftToReadMsg = 'You have ' + tokensLeftToRead + ' tokens of ' + totalTokens + ' left to read.'
      }     
    }
    return tokenAnnouncement;
  }

  function messageClassByAccuracy(accuracy){
    if (accuracy <= 0.2){return '_red'}
    if (accuracy > 0.2 && accuracy < 0.4) {return '_orange'}
    if (accuracy >= 0.4 && accuracy < 0.6) {return '_greenish'} else{
      return '_green'
    }
  }

  // parses the JSON object report into some prettified report to display in HTML
  function prettify(report) {
    var out = '';
    if (report.tokenCountMsg) {
      out += '<p class="message">'+report.tokenCountMsg+'</p>\n';
      
    }
    if (report.tokensLeftToReadMsg){
      out += '<p class="message">'+report.tokensLeftToReadMsg+'</p>\n';
    }

    if (report.status === 'processing' && report.avgAcc !== NaN) {
      out += '<p class="message '+messageClassByAccuracy(report.avgAcc)+
              '">Total average accuracy: '+util.percentage(report.avgAcc, 1, 3)+'%</p>';

      var modules = report.modules;
      for (var mod in modules) {
        if (!modules.hasOwnProperty(mod)) continue;

        var module = modules[mod];
        var accuracy = module.totalStats.accuracy;
        out += '<h3>'+mod+'</h3>';
        if (accuracy) {
          var message = messageClassByAccuracy(accuracy);
          
          out += '<p class="'+message+'">Average accuracy: '+util.percentage(accuracy, 1, 3)+'%</p>';
        }
        if (module.perRecordingStats) {
          out += '<h3>More stats</h3>';
          out += '<ul>';
          for (var i = 0; i < module.perRecordingStats.length; i++) {
            var acc = module.perRecordingStats[i].stats.accuracy;
            out += '    <li>Rec. '+i+', accuracy: '+util.percentage(acc, 1, 3)+'%</li>';
          }
          out += '</ul>';
        }
      }
    }
    
    return out;
  }
}
}());