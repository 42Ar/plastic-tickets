
var PlasticTickets = {};

PlasticTickets.PlasticTable = function (data, body_id) {
    var sort_btn = [];
    var cur_sort_btn = null;
    var cur_sort_mode = null;
    var cur_sort_func = null;
    this.filter_func = null;

    this.reset_sorting = function (){
        sort_btn.forEach(btn => btn.innerHTML = "⇵");
        cur_sort_btn = null;
        cur_sort_mode = null;
        cur_sort_func = null;
    }

    this.on_sort_click = function (clicked_btn, sort_func) {
        if (clicked_btn === cur_sort_btn) {
            if (clicked_btn.innerHTML === "🠗"){
                cur_sort_mode = "🠕";
                clicked_btn.innerHTML = "🠕";
            } else {
                this.reset_sorting();
            }
            clicked_btn.blur();
        } else if (clicked_btn !== null){
            this.reset_sorting();
            cur_sort_mode = "🠗";
            cur_sort_btn = clicked_btn;
            cur_sort_func = sort_func;
            clicked_btn.innerHTML = "🠗";
            clicked_btn.blur();
        }
    }

    this.rebuild = function () {
        var table = data.filter(this.filter_func);
        if (cur_sort_btn !== null) {
            var sort_dir = 1;
            if (cur_sort_mode === "🠕"){
                sort_dir = -1;
            }
            table.sort((a, b) => cur_sort_func(a, b, sort_dir));
        }
        var new_tbody = document.createElement(body_id);
        new_tbody.id = body_id; 
        table.forEach(row_data => row_builder(row_data, new_tbody.insertRow()));
        let old_tbody = document.getElementById(body_id);
        old_tbody.parentNode.replaceChild(new_tbody, old_tbody);
    }

    this.register_sort_button = function (button, sort_func) {
        button.innerHTML = "⇵";
        button.onclick = () => {
            this.on_sort_click(button, sort_func);
            this.rebuild();
        }
        sort_btn.push(button);
    }

    this.reset_sorting();
}

PlasticTickets.populate_with_options = function (element, opts) {
    opts.forEach(name => {
        var option = document.createElement("option");
        option.text = name;
        element.add(option);
    });
}

PlasticTickets.simple_sort_func = function (a, b, dir) {
    if (a === null && b === null) {
        return 0;
    } else if (a === null) {
        return dir;
    } else if (b === null) {
        return -dir;
    } else if (a > b) {
        return dir;
    } else if(a < b){
        return -dir;
    } else {
        return 0;
    }
}

PlasticTickets.get_selected_values = function (select) {
    // stolen from https://stackoverflow.com/questions/5866169/how-to-get-all-selected-values-of-a-multiple-select-box
    var result = [];
    var options = select && select.options;
    var opt;

    for (var i=0, iLen=options.length; i<iLen; i++) {
        opt = options[i];

        if (opt.selected) {
            result.push(opt.value || opt.text);
        }
    }
    return result;
}

