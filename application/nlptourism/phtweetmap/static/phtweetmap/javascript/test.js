$('button').on('click', function(e) {
    var li = $(this).closest('li');
    var pk = li.attr('data-pk');
    var buttons = $(this).closest('#buttons');
    if ($(this).attr('class') === 'tourism-button') {
        var actual_classification = 'tourism-act';
    } else {
        var actual_classification = 'nontourism-act';
    }
    $.ajax({
        url: '/set/' + actual_classification + '/' + pk,
        method: 'GET',
        success: function(data) {
            buttons.hide();
            li.addClass(actual_classification);
        }
    });
});

$('#results').on('click', function(e) {
    var truepos = $('li.tourism.tourism-act').length;
    var falsepos = $('li.tourism.nontourism-act').length;
    var trueneg = $('li.nontourism.nontourism-act').length;
    var falseneg = $('li.nontourism.tourism-act').length;

    var precision = 0;
    var recall = 0;
    var total = $('li').length;
    var accuracy = (truepos + trueneg) / total;

    if (truepos + falsepos != 0) {
        precision = truepos / (truepos + falsepos);
    }
    if (truepos + falseneg != 0) {
        recall = truepos / (truepos + falseneg);
    }
    if (precision + recall != 0) {
        var fscore = 2 * (precision * recall) / (precision + recall);
    }

    var div = $('<div></div>');
    $('body').append(div);
    div.append('truepos: ' + truepos + '</br>');
    div.append('falsepos: ' + falsepos + '</br>');
    div.append('trueneg: ' + trueneg + '</br>');
    div.append('falseneg: ' + falseneg + '</br>');
    div.append('accuracy: ' + accuracy + '</br>');
    div.append('precision: ' + precision + '</br>');
    div.append('recall: ' + recall + '</br>');
    div.append('fscore: ' + fscore + '</br>');
});