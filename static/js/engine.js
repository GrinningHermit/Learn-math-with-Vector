let current_number = '';

let menu_options = [
    ['add (+) 1 to 10', '+', 10],
    ['add (+) 1 to 20', '+', 20],
    ['add (+) 1 to 30', '+', 30],
    ['subtract (-) 1 to 10', '-', 10],
    ['subtract (-) 1 to 20', '-', 20],
    ['subtract (-) 1 to 30', '-', 30],
];


// sending and receiving json from server
getHttpRequest = function (url, dataSet)
{
    let xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
        if (xhr.readyState == XMLHttpRequest.DONE) {
            console.log(xhr.responseText);
            if(xhr.responseText == '+'){
                $('.enter').fadeTo('fast',1);
            }
            if(xhr.responseText == 'done'){
                $('#menu_overlay').show();
            }
        }
    };
    xhr.open('POST', url, true);
    xhr.send(JSON.stringify(dataSet));
};

function postHttpRequest(url, dataSet)
{
    let xhr = new XMLHttpRequest();
    xhr.open("POST", url, true);
    xhr.send( JSON.stringify( dataSet ) );
}

function createMenuButtons(value, index, array){
    $('#menu_overlay').append('<div id="menu_btn' + index + '" class="menu_btn flex-item">' + value[0] + '</div>');
    let btn = '#menu_btn' + index;
    $(btn).attr('num',index);
    $(btn).click(function (){
        // initiate vector
        let num = $(this).attr('num');
        let type = menu_options[num][1];
        let range = menu_options[num][2];
        console.log(type + ' ' +  range);
        getHttpRequest('game_start', {type, range});
        $('#menu_overlay').hide();
    });
}

$( function () {
    // menu setup
    menu_options.forEach(createMenuButtons);

    // numeric pad setup
    for (i = 0; i <10; i++){
        $('.numpad').append('<div id="num_' + i + '" class="number">' + i + '</div>');
        let num = '#num_' + i;
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

    $('.enter').fadeTo(0, 0.2);
    $('.enter').on('click', function() {
        getHttpRequest('answer', $('.result').text());
        current_number = '';
        $('.result').html('&nbsp;');
        $('.delete').css('opacity','0');
    });
});

