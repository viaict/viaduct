$(document).ready(function()
{
    $(".confirmation").click(function(ev)
    {
        //alert($('#confirmationModal')[0]);
        //$('#confirmationModal')[0].modal("show");

        if (!confirm("Weet je ZEKER dat je dit wilt doen?!")) 
        {
            ev.preventDefault();
        }
    });
})
