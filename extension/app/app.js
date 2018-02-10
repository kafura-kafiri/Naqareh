$(function() {
    var template = '#login-template';
    if (value = localStorage.apikey) {
        var apikey = value;
        template = '#calendar-template';
    }

    var ractive = Ractive({
        target: '#target',
        template: template,
        data: {
            key: apikey ? apikey : '',
            hours: [
                0, 1, 0, 2, 1, 0,
                1, 0, 2, 1, 0, 1,
                0, 2, 1, 0, 1, 0,
                2, 1, 0, 1, 0, 2,
            ],
            date: {
                year: 1396,
                month: 'esfand',
                day: 4
            }
        }
    });

    if(ractive.get('key') !== '') {
        var uri = '/' + ractive.get('key');
        $.get(uri, function(response) {
            ractive.set('hours', response.hours);
            ractive.set('date', response.date);
        });
    }

    ractive.on( 'login', function () {
        alert(this.get('key'));
        localStorage.apikey = this.get('key');
    });

    ractive.on( 'inc', function(event) {
        var index = event.node.getAttribute('data-index');
        index = parseInt(index);
        var value = ractive.get('hours.' + index);
        value ++;
        value %= 3;
        var date = ractive.get('date');
        var uri = '/' +
            ractive.get('key') + '/' +
            date.year + '/' +
            date.month + '/' +
            date.day + '/' +
            index + ':' + value;
        $.post(uri, function(response) {
            ractive.set('hours.' + index, value);
        });
    });
});
