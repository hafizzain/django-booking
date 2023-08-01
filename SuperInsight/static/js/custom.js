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