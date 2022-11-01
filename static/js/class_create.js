function remove_popup(times) {
  times.parentNode.parentNode.style.display = "none";
  times.parentNode.style.display = "none";
}

function submit_class() {
  all_students = [];
  all_questions = [];
  $(".new_student").each(function (i, obj) {
    student_name = $(obj).find("input").val();
    if (student_name != "") {
      all_students.push(student_name);
    }
  });
  $(".questions_created").each(function (i, obj) {
    question = $(obj).find(".question_input").val();
    type = $(obj).find(".question_select").val();
    all_questions.push(`${question}/${type}`);
  });
  $("#all_students_form").val(all_students.join("|"));
  $("#all_questions_form").val(all_questions.join("|"));
  $("#class_form").submit();
}

function validate(box) {
  if (box.checked) {
    document.getElementById("tardy_delay").style.display = "block";
  } else {
    document.getElementById("tardy_delay").style.display = "none";
  }
}

function add_student() {
  parent = document.querySelector(".student_container");
  template = document
    .getElementById("student_template")
    .content.cloneNode(true);
  parent.appendChild(template);
}

function add_question() {
  parent = document.querySelector(".question_container");
  template = document
    .getElementById("question_template")
    .content.cloneNode(true);
  parent.appendChild(template);
}

function remove_student(student) {
  student.parentNode.remove();
}

async function change_pin() {
  new_pin = Math.floor(Math.random() * 90000) + 10000;
  el = document.getElementById("pincode_changing").innerHTML = new_pin;
  changing_id = document.getElementById("current_class_pin").innerHTML;
  let response = await fetch(
    `/change_pin?changing=${changing_id}&pin=${new_pin}`
  );
  if (response.ok) {
    let pinJson = await response.json();
    console.log(pinJson);
  }
}

function add_popup() {
  document.querySelector("#popup_bg").style.display = "block";
  document.querySelector("#new_popup").style.display = "block";
}
function code_popup(pincode, class_id) {
  document.getElementById("current_class_pin").innerHTML = class_id;
  document.getElementById("pincode_changing").innerHTML = pincode;
  document.querySelector("#code_bg").style.display = "block";
  document.querySelector("#code_popup").style.display = "block";
}
