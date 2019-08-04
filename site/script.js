/*
[Key Symbols]
Name -> @
P1 -> #
P2 -> $
P3 -> %
P4 -> ^
*/

let genderPronouns = {
    "M":["he", "his", "him", "his"], //#, $, %, ^
    "F":["she", "her" , "her", "hers"],
    "T":["they", "their" , "them", "theirs"]
}
    
document.getElementById("submit").addEventListener("click", function() {
    let options = document.getElementsByClassName("sentence_option")
    
    let studentName = document.getElementById("student_name").value
    let studentPronouns = genderPronouns[document.getElementById("student_gender").value]

    let reportArea = document.getElementById("generated_report")
    let generatedReport = ""
    if(studentName) {
        for(let i = 0; i < options.length; i++) {
            generatedReport += subtituteGenerics(options[i].value, studentName, studentPronouns) + " "        
        }
        reportArea.value = generatedReport
    } else {
        alert("Student needs to have a name!")
    }
})

function subtituteGenerics(str, name, pronouns) {
    str = str.trim().replace()
        .replace("@", name)
        .replace("#", pronouns[0])
        .replace("$", pronouns[1])
        .replace("%", pronouns[2])
        .replace("^", pronouns[3]) + " "
    
    let capitalizationIndices = []
    for(let i = 0; i < str.length; i++) {
        if(str[i] == "." || str[i] == "!" || str[i] == "?") capitalizationIndices.push(i)
    }
    for(index of capitalizationIndices) {
        if(index + 2 < str.length) {
            str = str.slice(0, index + 2) + str.charAt(index+2).toUpperCase() + str.slice(index + 3, str.length)
        }
    }

    return str.trim()
}