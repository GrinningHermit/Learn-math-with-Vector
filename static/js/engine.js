// let sum = sumX + ' + ' + sumY + ' = ';

let current_number = '';

function postHttpRequest(url, dataSet)
{
    let xhr = new XMLHttpRequest();
    xhr.open("POST", url, true);
    xhr.send( JSON.stringify( dataSet ) );
}

$( function () {
    for (i = 0; i <10; i++){
        $('.numpad').append('<div id="num_' + i + '" class="number">' + i + '</div>');
        num = '#num_' + i;
        $(num).click(function (){
            current_number += $(this).text();
            $('.result').html(current_number);
            $('.delete').css('opacity','1');
        });
    }
    $('#num_0').after('<div class="enter">enter</div>');
    $('.delete').click(function(){
        current_number = '';
        $('.result').html('&nbsp;');
        $('.delete').css('opacity','0');
    });


    $('.enter').on('click', function() {
        postHttpRequest('answer', $('.result').text());
        current_number = '';
        $('.result').html('&nbsp;');
        $('.delete').css('opacity','0');
    });
});

