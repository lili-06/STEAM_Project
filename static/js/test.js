//const age = 18; //nie można zmieniać tej zmiennej
let myAge = 16; //tą można

let age = prompt("Podaj wiek");

function checkAge (age) {
    if (age >= 18) {
        console.log('Jestem pełnoletnia');
    } else {
        console.log('Jestem niepełnoletnia');
    }
}

checkAge(19);
checkAge(myAge);
checkAge(age);