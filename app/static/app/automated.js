document.addEventListener('DOMContentLoaded', () => {
  // get poem and scansion from the HTML
  document.querySelector('#algorithm').addEventListener('input', reload);
  reload();
  document.querySelector('#go').addEventListener('click', () => {
    let url = document.querySelector('#go-to-page').value;
    if (url != 'none') {
            window.location = url;
        }
  });
});

function reload() {
  let scansionType = document.getElementById('algorithm').value;
  const about = document.querySelectorAll('.about-algorithm');
  if (about) {
    about.forEach((element) => {
      element.style.display = 'none'
    })
  }
  document.getElementById(`about-${scansionType}`).style.display = 'inline-block';
  const tables = document.querySelectorAll('table')
  if (tables) {
    tables.forEach((element) => {
    element.remove()
    })
  }
  const poem = document.querySelector('#poem-text').textContent;
  let scansion = document.getElementById(`${scansionType}`).textContent;
  // split poem and chosen scansion into lines
  let lines = poem.split(/\r\n|\n|\r/);
  console.log(lines);
  let scansion_lines = scansion.split(/\r\n|\n|\r/);
  console.log(scansion_lines);
  // loop through the the lines
  for (let i = 0; i < lines.length; i++) {
    //remove any extra space from beginning and end of lines
    lines[i] = lines[i].trim()
    // if the line is not empty, start processing it
    if (lines[i]) {
      // split poem line on spaces
      let words = lines[i].split(/\s+/);
      // remove leading and trailing from corresponding line of scansion and split it on spaces
      scansion_lines[i] = scansion_lines[i].trim()
      let scanned_words = scansion_lines[i].split(/\s+/);
      // create a table to hold each line
      let table = document.createElement('table');
      // identify it by its corresponding line
      table.setAttribute('id', `line${i}`);
      table.setAttribute('class', 'autoline');
      // create two rows in the table, one for stress patterns, one for words
      table.innerHTML = `<tr class="stress-pattern"></tr>
                         <tr class="words"></tr>`;
      // append this table to the div intended for the poem to be scanned and assign each row to a variable
      document.querySelector('#poem-to-scan').append(table);
      let stress = table.querySelector(".stress-pattern");
      let wordRow = table.querySelector(".words");
      // loop through the words in each line
      for (let j = 0; j < words.length; j++) {
        // for each word, create a cell and give it an id indicating where it falls and the purpose it serves
        let scansion = document.createElement('td');
        scansion.setAttribute('id', `scansion${i}-${j}`);
        scansion.setAttribute('class', 'autoscansion');
        // append this cell to the scansion row
        stress.append(scansion);
        // if the scansion has a corresponding "word," add symbols to the cell to represent each syllable
        if (scanned_words[j]) {
          // loop through each syllable (indicated by a symbol) in the scansion
          for (let k = 0; k < scanned_words[j].length; k++) {
            // create a span for each syllable and assign it a class of "symbol"
            let symbol = document.createElement('span');
            symbol.setAttribute('class', 'autosymbol')
            // if the user is promoted (i.e., has authority to scan previously un-scanned poems), show the previous scasion, symbol by symbol, in the cell above the word
            symbol.textContent = `${scanned_words[j][k]}`;
            // append the symbol to the cell
            scansion.append(symbol);
          }
        }
        // next, find the word corresponding to the scansion, create a table cell for it, add it to the cell, and append the cell to the row for words
        let word = document.createElement('td');
        word.setAttribute('id', `word${i}-${j}`);
        word.setAttribute('class', 'word');
        word.textContent = words[j];
        wordRow.append(word);
      }
    // if the row is empty, insert an empty table for the stanza break
    } else {
      table = document.createElement('table');
      table.innerHTML = '<tr></tr><tr></tr>'
      table.setAttribute('class', 'empty')
      document.querySelector('#poem-to-scan').append(table);
    }
  }
}
