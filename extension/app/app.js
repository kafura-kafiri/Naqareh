$(function() {
    var template = '#login-template';
    var base_uri = 'http://localhost:5000'
    if (value = localStorage.apikey) {
        var apikey = value;
        template = '#calendar-template';
    }

    var ractive = Ractive({
        target: '#target',
        template: template,
        data: {
            username: '',
            password: '',
            key: apikey ? apikey : '',
            hours: [
                0, 1, 0, 2, 1, 0,
                1, 0, 2, 1, 0, 1,
                0, 2, 1, 0, 1, 0,
                2, 1, 0, 1, 0, 2,
            ],
            date: {
                year: 1396,
                month: 'esfand', // need to pretify() -> ractive
                day: 4,
            },
            format: function(i) {
                return {
                    1: 'farvardin',
                    2: 'ordibehesht',
                    3: 'khordad',
                    4: 'tir',
                    5: 'mordad',
                    6: 'shahrivar',
                    7: 'mehr',
                    8: 'aban',
                    9: 'azar',
                    10: 'dei',
                    11: 'bahman',
                    12: 'esfand',
                }[i];
            },
            format_label: function(h) {
                if (h < 10) return '0' + h;
                return h;
            },
            label: 1
        }
    });

    if(ractive.get('key') != '') {
        var uri = base_uri + '/' + ractive.get('key');
        $.get(uri, function(response) {
            ractive.set('hours', response.hours);
            ractive.set('date', response.date);
        });
    }

    ractive.on( 'login', function () {
        username = this.get('username');
        password = this.get('password');
        $.get(base_uri + '/' + username + ':' + password, function(key) {
            ractive.set('key', key);
            localStorage.apikey = ractive.get('key');
            ractive.resetTemplate('#calendar-template');
        });
    });

    ractive.on( 'inc', function(event) {
        var index = event.node.getAttribute('data-index');
        index = parseInt(index);
        var value = ractive.get('hours.' + index);
        value ++;
        value %= 3;
        var date = ractive.get('date');
        var uri = base_uri + '/' +
            ractive.get('key') + '/' +
            date.year + '/' +
            date.month + '/' +
            date.day + '/' +
            index + ':' + value;
        $.post(uri, function(response) {
            ractive.set('hours.' + index, value);
        });
    });

    ractive.on( 'hour', function(event) {
        var index = event.node.getAttribute('data-index');
        index = parseInt(index);
        hour = (index + 6) % 24;
        hour -= hour % 6;
        this.set('label', hour);
    });
});
