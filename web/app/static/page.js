//定义函数
window.Clipboard = (function (window, document, navigator) {
    var textArea,
        copy;

    // 判断是不是ios端
    function isOS() {
        return navigator.userAgent.match(/ipad|iphone/i);
    }
    //创建文本元素
    function createTextArea(text) {
        textArea = document.createElement('textArea');
        textArea.value = text;
        document.body.appendChild(textArea);
    }
    //选择内容
    function selectText() {
        var range,
            selection;

        if (isOS()) {
            range = document.createRange();
            range.selectNodeContents(textArea);
            selection = window.getSelection();
            selection.removeAllRanges();
            selection.addRange(range);
            textArea.setSelectionRange(0, 999999);
        } else {
            textArea.select();
        }
    }

    //复制到剪贴板
    function copyToClipboard() {
        try {
            if (document.execCommand("Copy")) {
                alert("复制成功！");
            } else {
                alert("复制失败！请手动复制！");
            }
        } catch (err) {
            alert("复制错误！请手动复制！")
        }
        document.body.removeChild(textArea);
    }

    copy = function (text) {
        createTextArea(text);
        selectText();
        copyToClipboard();
    };

    return {
        copy: copy
    };
})(window, document, navigator);

//使用函数
$("#copy").click(function () {
    var val = $("#textAreas").val();
    Clipboard.copy(val);
});
