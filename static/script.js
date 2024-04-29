function monitor_update() {
    let types = [];
    let periods = [];
    
    $("#add_table select").each(function(index, element) {
        if($(element).hasClass("type")) {
            types.push($(element).val());
        }
        if($(element).hasClass("period")) {
            periods.push($(element).val());
        }
    });

    fetch("/monitor", {
        method: "POST",
        headers: {
            'Content-Type': 'application/json'
        },
        cache: 'no-cache',
        body: JSON.stringify({
            types: types,
            periods: periods
        })
    })
    .then((response) => response.blob())
    .then((blob) => {
        const objectURL = URL.createObjectURL(blob);
        $("#graph").attr("src", objectURL);
    });
}

function trigger_update() {
    let types = [];
    let metrics = [];
    let thresholds = [];
    
    $("#trigger_table select").each(function(index, element) {
        if($(element).hasClass("alarm")) {
            types.push($(element).val());
        }
        if($(element).hasClass("metric")) {
            metrics.push($(element).val());
        }
    });

    $(".threshold").each(function(index, element) {
        thresholds.push($(element).val());
    });

    fetch("/trigger", {
        method: "POST",
        headers: {
            'Content-Type': 'application/json'
        },
        cache: 'no-cache',
        body: JSON.stringify({
            types: types,
            metrics: metrics,
            thresholds: thresholds
        })
    }).then((response) => {
        monitor_update();
    });
}

monitor_update();

$(document).ready(function() {
    $('#add_table .add_row').click(function() {
        row = `
        <tr>
            <td colspan="2">
                <select class="form-select type">
                    <option selected value="cpu">CPU Utilization</option>
                    <option value="memory">Memory Usage</option>
                </select>
            </td>
            <td>
                <select class="form-select period">
                    <option selected value="1">1 Minute</option>
                    <option value="5">5 Minutes</option>
                </select>
            </td>
            <td>
                <button type="button" class="btn btn-danger w-100 delete_row">삭제</button>
            </td>
        </tr>
        `;
        $("#add_table tbody").append(row);
    });

    $('#trigger_table .add_row').click(function() {
        row = `
        <tr>
            <td>
                <select class="form-select alarm">
                    <option selected value="alert">Alert</option>
                </select>
            </td>
            <td>
                <select class="form-select metric">
                    <option selected value="cpu">CPU Utilization</option>
                    <option value="memory">Memory Usage</option>
                </select>
            </td>
            <td>
                <input type="number" class="form-control threshold" value="1" />
            </td>
            <td>
                <button type="button" class="btn btn-danger w-100 delete_row">삭제</button>
            </td>
        </tr>
        `;
        $("#trigger_table tbody").append(row);
    });

    $("#add_table,#trigger_table").on('click', '.delete_row', function() {
        $(this).closest('tr').remove();
    });

    $("#adds").click(monitor_update);
    $("#trigger").click(trigger_update);
});