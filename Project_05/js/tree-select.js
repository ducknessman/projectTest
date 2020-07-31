/**
 * 下拉树
 * 务必先引入 jQuery 和 zTree
 */
(function ($) {

    function TreeSelect() {
        var ts = new Object();
        ts.key = "xxx";
        ts.$input = null;
        ts.$selDiv = null;
        ts.$selUl = null;
        ts.$zTree = null;

        /**
         * 初始化下拉树
         * @param key
         * @param data
         */
        ts.initialize = function (key, data) {
            ts.key = key;
            ts.initInput();
            ts.initTree(data);

            ts.$input.bind("keyup", function () {
                ts.changeInput();
            });

            $("body").bind("click", ts.bodyClick);
        };

        /**
         * 初始化输入框
         */
        ts.initInput = function () {
            ts.$input = $("#" + ts.key);
            var input_w = ts.$input.width();
            var input_h = ts.$input.height();

            ts.$input.parent().css({
                "position": "relative",
                "display": "inline-block",
                "min-width": input_w,
                "min-height": input_h,
                "margin": "auto",
                "vertical-align": "middle"
            });
            ts.$input.css({
                "position": "absolute",
                "margin-left": "2px"
            });

            ts.$input.bind("focus", function () {
                ts.openTree();
            });

        };

        /**
         * 初始化树结构
         * @param data
         */
        ts.initTree = function (data) {
            var window_h = $(window).height();

            var input_x = ts.$input.offset().left;
            var input_y = ts.$input.offset().top;
            var input_w = ts.$input.outerWidth();
            var input_h = ts.$input.outerHeight();
            var div_w = input_w;
            var div_max_h = (window_h - input_y - input_h) * 0.8;

            var html = '<div id="sel_div_' + ts.key + '">' +
                '<ul id="sel_ul_' + ts.key + '" class="ztree"></ul>' +
                '</div>';
            ts.$input.after(html);

            ts.$selDiv = $("#sel_div_" + ts.key);
            ts.$selDiv.offset({
                "left": input_x,
                "top": input_y + input_h + 1//1px的缝隙
            });
            ts.$selDiv.css({
                "position": "absolute",
                "width": div_w,
                "max-width": div_w,
                "max-height": div_max_h,
                "overflow-x": "auto",
                "overflow-y": "auto",
                "background-color": "#F7F7F7",
                "z-index": 2147483647
            });

            ts.$selUl = $("#sel_ul_" + ts.key);
            ts.$selUl.css({
                "margin": 0,
                "padding": 0
            });

            $.fn.zTree.init(ts.$selUl, {
                callback: {
                    onClick: ts.clickTree
                },
                view: {
                    showLine: true,
                    showTitle: true,
                    selectedMulti: false,
                    expandSpeed: "fast"
                },
                data: {
                    key: {
                        name: "name"
                    },
                    simpleData: {
                        enable: true,
                        idKey: "id",
                        pIdKey: "pid"
                    }
                }
            }, data);

            ts.$zTree = $.fn.zTree.getZTreeObj("sel_ul_" + ts.key);
        };

        /**
         * 改变输入值
         */
        ts.changeInput = function () {
            var input_val = ts.$input.val();
            input_val = input_val.trim().toLowerCase();
            if ("" == input_val) {
                ts.$zTree.expandAll(false);
                return;
            }

            var findNode = ts.$zTree.getNodesByFilter(function (node) {
                if (node && node["name"].toLowerCase().indexOf(input_val) > -1) {
                    ts.$zTree.selectNode(node, false);//单一选中
                    return true;
                }
                return false;
            }, true);//只找第一个

            if (findNode && !findNode.isParent) {
                var parentNode = findNode.getParentNode();
                var expands = new Set();
                do {//展开符合的节点及其父、祖节点
                    expands.add(parentNode["id"]);
                    ts.$zTree.expandNode(parentNode, true, false, true);
                    parentNode = parentNode.getParentNode();
                } while (parentNode);

                var openNodes = ts.$zTree.getNodesByFilter(function (node) {
                    if (node && node.isParent && node.open && !expands.has(node["id"])) {
                        return true;
                    }
                    return false;
                }, false);//找一群
                if (openNodes && openNodes.length > 0) {
                    for (var i = 0; i < openNodes.length; i++) {
                        //关闭不符合的其他父节点
                        ts.$zTree.expandNode(openNodes[i], false, true, false);
                    }
                }
            } else {
                ts.$zTree.expandAll(false);
            }
        };

        /**
         * 点击树节点
         */
        ts.clickTree = function (event, treeId, treeNode) {
            if (treeNode && !treeNode.isParent) {
                ts.$input.val(treeNode["name"]);
                ts.closeTree();
            }
        };

        /**
         * 点击输入框和树结构之外的部分
         * @param event
         */
        ts.bodyClick = function (event) {
            var x1 = ts.$input.offset().left;
            var y1 = ts.$input.offset().top;
            var width = ts.$input.outerWidth();
            var height = ts.$input.outerHeight() + ts.$selDiv.outerHeight() + 1;//1px的缝隙
            var x2 = x1 + width;
            var y2 = y1 + height;

            var x = event.clientX;
            var y = event.clientY;
            if (x < x1 || x2 < x || y < y1 || y2 < y) {
                ts.closeTree();
            }
        };

        /**
         * 关闭树结构
         */
        ts.closeTree = function () {
            ts.$selDiv.hide();
        };

        /**
         * 展开数节点
         * @param key
         * @param options
         */
        ts.openTree = function () {
            ts.$selDiv.show();
        };

        /**
         * 树结构位置微调
         */
        ts.treeOffset = function () {
            //TODO
        };

        return ts;
    }

    /**
     * 主调方法
     * @param data
     * @returns {TreeSelect}
     */
    $.fn.treeSelect = function (data) {
        var key = this.attr("id");

        var ts = new TreeSelect();
        ts.initialize(key, data);
        ts.closeTree();

        return ts;
    }

})(jQuery);