let sum = sumX + ' + ' + sumY + ' = ';

let timeout = function(){
    $('#answer').click();
}

function postHttpRequest(url, dataSet)
{
    let xhr = new XMLHttpRequest();
    xhr.open("POST", url, true);
    xhr.send( JSON.stringify( dataSet ) );
}

$( function () {
    $('#content').prepend(sum);
    $('#answer').numpad()
    setTimeout(timeout, 100);

    $('#answer').on('change', function() {
        postHttpRequest('answer', $(this).val()); 
     });
});

