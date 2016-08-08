$(document).ready(function(){
    $(".header-nav>ul>li").bind('mouseover',function(){
        $(this).children('div').slideDown('fast');
        $(this).addClass('active');
    }).bind('mouseleave',function()
    {
        $(this).children('div').slideUp('fast');
        $(this).removeClass('active');
    });

});