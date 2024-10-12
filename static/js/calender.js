$(document).ready(function() {
    $('#calendar').fullCalendar({
        header: {
            left: 'prev, next',
            center: 'title',
            right: ''
        },
        editable: true,
        dayClick: function(date) {
            if (!date.isBefore(moment(), 'day')) {
                $.ajax({
                    url: '/add_date',
                    type: 'POST',
                    data: {
                        date: date.format()
                    },
                    success: function(response) {
                        console.log('Date added:', response);
                        // redirect to show_data page
                        window.location.href = '/show_data?date=' + encodeURIComponent(response.date);
                    },
                    error: function(error) {
                        console.log('Error:', error);
                    }
                });
            } else {
                console.log('Cannot select past dates');
            }
        },
        dayRender: function(date, cell) {
            if (date.isBefore(moment(), 'day')) {
                cell.addClass('fc-past');
            }
        },
    });

    $('#calendar').on('mouseenter', '.fc-day', function() {
        $(this).addClass('hover-highlight');
    }).on('mouseleave', '.fc-day', function() {
        $(this).removeClass('hover-highlight');
    });
});
