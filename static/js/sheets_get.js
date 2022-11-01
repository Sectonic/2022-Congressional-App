function getDate() {
  let yourDate = new Date();
  const offset = yourDate.getTimezoneOffset();
  yourDate = new Date(yourDate.getTime() - offset * 60 * 1000);
  return yourDate.toISOString().split("T")[0];
}

document.getElementById("date_select").value = getDate();

var current_date = getDate();
var current_class = $(".class_select").find("option:first-child").val();
var current_students;
var all_students;
var current_questions;
var pie_data = [];
var num_arr = [];

var options = {
  series: [
    {
      name: "Students",
      data: [5, 5, 3],
    },
  ],
  chart: {
    height: 350,
    type: "line",
    zoom: {
      enabled: false,
    },
  },
  xaxis: {
    title: "Minutes",
  },
  dataLabels: {
    enabled: false,
  },
  stroke: {
    curve: "straight",
    colors: ["#ee5a4f"],
  },
  title: {
    text: "Attendance Submitted Per Minute",
    align: "left",
  },
  grid: {
    row: {
      colors: ["#f3f3f3", "transparent"],
      opacity: 0.5,
    },
  },
  xaxis: {
    categories: num_arr,
  },
};

var options2 = {
  series: [64, 1, 2],
  chart: {
    id: "pie_chart",
    width: 380,
    type: "pie",
  },
  labels: ["On-time", "Tardy", "Absent"],
  responsive: [
    {
      breakpoint: 480,
      options: {
        chart: {
          width: 200,
        },
        legend: {
          position: "bottom",
        },
      },
    },
  ],
  colors: ["#36dd87", "#f0c742", "#ee5a4f"],
};

for (let i = 0; i < 90; i++) {
  num_arr.push(i);
}

function changeClass(class_val) {
  current_class = $(class_val).val();
  changeSheets_add();
}

function changeDate() {
  current_date = document.getElementById("date_select").value;
  changeSheets_add();
}

function print_el() {
  $(".sheets_attendance").print();
}

var chart = new ApexCharts(document.querySelector("#chart"), options);
chart.render();

var chart2 = new ApexCharts(document.querySelector("#chart_2"), options2);
chart2.render();

function changeSheets() {
  fetch("../static/json/data.json")
    .then((response) => response.json())
    .then((data) => {
      sheets_data(data, "interval");
    });
}

function changeSheets_add() {
  fetch("../static/json/data.json")
    .then((response) => response.json())
    .then((data) => {
      sheets_data(data, "change");
    });
}

async function sheets_data(json, type) {
  $("#attendance_body").empty();
  if (current_date in json) {
    if (current_class in json[current_date]) {
      current_table = json[current_date][current_class]["data"];
      current_info = json[current_date][current_class]["info"];
    }
  }
  if (type == "change") {
    let response = await fetch(`/get_students?class=${current_class}`);
    let studentJson = await response.json();
    current_students = studentJson["students"];
    current_questions = studentJson["questions"];
    all_students = current_students;
    $("#start_time").html(studentJson["start"]);
    $("#end_time").html(studentJson["end"]);
  }
  var minutes_arr = [];
  if (current_date in json) {
    if (current_class in json[current_date]) {
      for (let i = 0; i < current_table.length; i++) {
        var tr = $("<tr></tr>");
        tr.attr("id", `${current_table[i]["name"]}_row`);
        for (const [key, value] of Object.entries(current_table[i])) {
          var td = $("<td></td>");
          if (key == "attendance") {
            if (value) {
              td.text("Present");
              td.attr("class", "present");
            } else {
              absent_total += 1;
              td.text("Absent");
              td.attr("class", "absent");
            }
          } else if (key == "submitted_time") {
            minutes_arr.push(value);
            td.text(value + " minutes");
            if (value > current_info["tardy_delay"]) {
              td.attr("class", "tardy");
            }
          } else {
            td.text(value);
          }
          tr.append(td);
        }
        $("#attendance_body").prepend(tr);
      }
    }
  }
  for (let i = 0; i < all_students.length; i++) {
    if (document.getElementById(`${all_students[i]}_row`) == null) {
      let tr = $("<tr></tr>");
      tr.attr("id", `${all_students[i]}_table`);
      let td1 = $("<td></td>");
      td1.text(all_students[i]);
      let td2 = $("<td></td>");
      td2.text("Absent");
      td2.attr("class", "absent");
      let td3 = $("<td></td>");
      td3.text("Not Submitted");
      let td4 = $("<td></td>");
      td4.text("");
      tr.append(td1, td2, td3, td4);
      $("#attendance_body").append(tr);
    }
  }
  for (let i = 0; i < current_questions.length; i++) {
    $("#custom_question").each(function () {
      $(this).remove();
    });
    let th = $("<th></th>");
    th.text(current_questions[i]);
    th.attr("id", "custom_question");
    $("#attendance_head").append(th);
  }
  chart_data = [];
  for (let j = 0; j <= Math.max(...minutes_arr); j++) {
    chart_data.push(minutes_arr.filter((x) => x == j).length);
  }
  chart.updateOptions({
    series: [
      {
        data: chart_data,
      },
    ],
  });
  (present_total = 0), (tardy_total = 0), (absent_total = 0);
  $("#attendance_body")
    .children("tr")
    .each(function () {
      console.log($(this).children().eq(1).next().attr("class"));
      if ($(this).children().eq(1).next().attr("class")) {
        tardy_total += 1;
      } else {
        if ($(this).children().eq(1).attr("class") == "present") {
          present_total += 1;
        } else {
          absent_total += 1;
        }
      }
    });
  pie_data = [present_total, tardy_total, absent_total];
  chart2.updateOptions({
    series: pie_data,
  });
}

changeSheets_add();
setInterval(changeSheets, 2000);
