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
  const scansionType = document.getElementById('algorithm').value;
  displayCorrectAbout(scansionType);

  // remove any existing scansion
  const tables = document.querySelectorAll('table')
  if (tables) {
    tables.forEach((element) => {
    element.remove()
    })
  }

  const poem = document.querySelector('#poem-text').textContent;
  const scansion = document.getElementById(`${scansionType}`).textContent;

  const lines = splitIntoLines(poem);
  const scansionLines = splitIntoLines(scansion);
  
  if (lines.length != scansionLines.length) {
    console.log("Mismatch in length between poem and scansion.")
  }
    // loop through lines and render each line so users can see scansions
  for (let i = 0; i < lines.length; i++) {
    if (lines[i]) {
      const words = splitIntoWords(lines[i]);
      const scannedWords = splitIntoWords(scansionLines[i]);

      if (words.length != scannedWords.length) {
        console.log(`Mismatch in number of words between poem and scansion in line ${i}`);
      }
      document.querySelector('#poem-to-scan').append(renderLine(words, scannedWords));
    // if line is empty, render an empty table
    } else {
      table = document.createElement('table');
      table.innerHTML = '<tr></tr><tr></tr>'
      table.setAttribute('class', 'empty')
      document.querySelector('#poem-to-scan').append(table);
    }
  }
}

function renderLine(words, scansions, lineNumber) {
  // create a table to hold each line
  let table = document.createElement('table');
  
  // identify it by its corresponding line
  table.setAttribute('id', `line${lineNumber}`);
  table.setAttribute('class', 'autoline');
  
  // create two rows in the table, one for stress patterns, one for words
  const stressRow = document.createElement('tr');
  stressRow.setAttribute('class', 'stress-pattern');
  table.append(stressRow);
  const wordRow = document.createElement('tr');
  wordRow.setAttribute('class', 'words')
  table.append(wordRow);
  
  // loop through the words in each line
  for (let j = 0; j < words.length; j++) {
    // for each word, create a cell and give it an id indicating where it falls and the purpose it serves
    stressRow.append(renderScansionCell(scansions[j], lineNumber, j));
    // next, find the word corresponding to the scansion, create a table cell for it, add it to the cell, and append the cell to the row for words
    wordRow.append(renderWordCell(words[j], lineNumber, j));
    // pronunciations change over time and between dialects, and the automated syllable makes mistakes as well; accordingly,
    // users should be able to add syllables to words or remove them; create a cell for plus and minus buttons, assign it the appropriate id and class, and append it to the third row of the table.
  }
  return table;
}

function renderScansionCell(scansion, lineNumber, wordNumber) {
  const scanCell = document.createElement('td');
  scanCell.setAttribute('id', `scansion${lineNumber}-${wordNumber}`);
  scanCell.setAttribute('class', 'autoscansion');
  for (let k = 0; k < scansion.length; k++) {
    // create a span for each syllable and assign it a class of "symbol"
    let symbol = document.createElement('span');
    symbol.setAttribute('class', 'autosymbol')
    // if the user is promoted (i.e., has authority to scan previously un-scanned poems), show the previous scasion, symbol by symbol, in the cell above the word
    symbol.textContent = `${scansion[k]}`;
    // append the symbol to the cell
    scanCell.append(symbol);
  }
  return scanCell;
}

function renderWordCell(word, lineNumber, wordNumber) {
  const wordCell = document.createElement('td');
  wordCell.setAttribute('id', `word${lineNumber}-${wordNumber}`);
  wordCell.setAttribute('class', 'word');
  wordCell.textContent = word;
  return wordCell;
}


function splitIntoLines(poemOrScansion) {
  return poemOrScansion.split(/\r\n|\n|\r/);
}

function splitIntoWords(line) {
  return line.trim().split(/\s+/)
}

function displayCorrectAbout(scansionType) {
  const about = document.querySelectorAll('.about-algorithm');
  if (about) {
    about.forEach((element) => {
      element.style.display = 'none';
    })
  }
  document.getElementById(`about-${scansionType}`).style.display = 'inline-block';
}