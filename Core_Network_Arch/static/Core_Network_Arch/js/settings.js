$(document).ready(function(){
    jAlert('这是一个可自定义样式的警告对话框', '警告对话框');
    $(".remove_type").click(function(){
        var elem = $(this).closest('.item');
        $.messager.confirm({
            'title':'Delete Confirmation',
            'message':'Sure?',
            'buttons': {
                'Yes' : {
                    'class' : 'blue',
                    'action': function(){
                        elem.slideUp();
                    }
                },
                'No' : {
                    'class' : 'gray'
                }
            }
        }
        )
    })

});