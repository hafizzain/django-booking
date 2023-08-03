let edit_btn = document.querySelectorAll('.edit_btn');
let close_btn = document.querySelectorAll('.close_btn');

function popup_handler(Main_BTN) {
    Main_BTN.forEach((btn, i) => {
        btn.addEventListener('click', () => {
            let popup = document.querySelectorAll('.popup')[i];
            if (popup) {
                popup.classList.toggle('hidden');
            }
        })
    })
}
popup_handler(close_btn)
popup_handler(edit_btn)


let all = document.querySelectorAll(".editor");
  all.forEach((ele, i) => {
    var quill = new Quill(ele, {
      theme: "snow",
      modules: {
        toolbar: [
          [{ header: [1, 2, false] }],
          ["bold", "italic", "underline", "link"],
          [{ list: "ordered" }, { list: "bullet" }],
          ["image"],
        ],
      },
    });
    console.log(document.querySelectorAll(".editorContentInput")[i]);
    if (document.querySelectorAll(".editorContentInput")[i]) {
      quill.on("text-change", function () {
        var editorContent = quill.root.innerHTML;
        document.querySelectorAll(".editorContentInput")[i].value =
          editorContent;
      });
    }
  });   