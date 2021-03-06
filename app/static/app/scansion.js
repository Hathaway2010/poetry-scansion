document.addEventListener('DOMContentLoaded', () => {
  // render poem so users can adjust scansions

  // get poem and scansion from the HTML
  const poem = document.querySelector('#poem-text').textContent
  const scansion = document.querySelector('.scansion-text').textContent

  const lines = splitIntoLines(poem);
  const scansionLines = splitIntoLines(scansion);
  
  if (lines.length != scansionLines.length) {
    console.log('Mismatch in number of lines between poem and scansion');
  };

  // loop through lines and render each line so users can adjust scansions
  for (let i = 0; i < lines.length; i++) {
    if (lines[i]) {
      const words = splitIntoWords(lines[i])
      const scannedWords = splitIntoWords(scansionLines[i]);
      if (words.length != scannedWords.length) {
        console.log(`Mismatch in number of words between poem and scansion in line ${i}`);
      }
      document.getElementById('poem-to-scan').append(renderLineInterface(words, scannedWords, i));
    
    // if the line is empty, insert an empty table for the stanza break
    } else {
      table = document.createElement('table');
      table.innerHTML = '<tr></tr><tr></tr>'
      table.setAttribute('class', 'empty')
      document.querySelector('#poem-to-scan').append(table);
    }
  }
  // add a submit button
  const button = document.createElement('button');
  button.setAttribute('id', 'submit-scansion');
  button.textContent = 'Scan Poem'
  button.addEventListener('click', submitScansion);
  document.querySelector('#poem-to-scan').append(button);

  // return to normal size if something outside a word is clicked on, make the word if it or its controls are clicked on
  document.querySelector('.container').addEventListener('click', (event) => {
    grow(event.target);
  });

  // turn tooltips into alerts for smaller screens 
  if (window.innerWidth < 600) {
    scinstructions = document.getElementById('sctooltip').textContent;
    alert(scinstructions);
    pminstructions = document.getElementById('pmtooltip').textContent;
    alert(pminstructions);
    document.querySelector('.container').addEventListener('click', (event) => {
      if (event.target.className == "word") {
        showControls(event);
      } else {
        hideControls()
      }
    });
  }
  // make dropdown menu work for small screens
  document.querySelector('#go').addEventListener('click', () => {
    let url = document.querySelector('#go-to-page').value;
    if (url != 'none') {
            window.location = url;
    }
  });
});

function renderLineInterface(words, scansions, lineNumber) {
  // create a table to hold each line
  let table = document.createElement('table');
  // identify it by its corresponding line
  table.setAttribute('id', `line${lineNumber}`);
  // append this table to the div intended for the poem to be scanned and assign each row to a variable
  document.querySelector('#poem-to-scan').append(table);
  
  // create and append to the table three rows, one for stress patterns, one for words, and one for buttons to remove or add syllables
  const stressRow = document.createElement('tr');
  stressRow.setAttribute('class', 'stress-pattern');
  table.append(stressRow);
  const wordRow = document.createElement('tr');
  wordRow.setAttribute('class', 'words')
  table.append(wordRow);
  const plusMinusRow = document.createElement('tr');
  plusMinusRow.setAttribute('class', 'plus-minus');
  table.append(plusMinusRow);

  // loop through the words in each line
  for (let j = 0; j < words.length; j++) {
    // for each word, create a cell and give it an id indicating where it falls and the purpose it serves
    stressRow.append(renderScansionCell(scansions[j], lineNumber, j));
    // next, find the word corresponding to the scansion, create a table cell for it, add it to the cell, and append the cell to the row for words
    wordRow.append(renderWordCell(words[j], lineNumber, j));
    // pronunciations change over time and between dialects, and the automated syllable makes mistakes as well; accordingly,
    // users should be able to add syllables to words or remove them; create a cell for plus and minus buttons, assign it the appropriate id and class, and append it to the third row of the table.
    plusMinusRow.append(renderPlusMinusCell(lineNumber, j));
  }
  return table
}

function renderScansionCell(scansion, lineNumber, wordNumber) {
  const scanCell = document.createElement('td');
  scanCell.setAttribute('id', `scansion${lineNumber}-${wordNumber}`);
  scanCell.setAttribute('class', 'scansion');
  // loop through each syllable (indicated by a symbol) in the scansion
  for (let k = 0; k < scansion.length; k++) {
    // create a span for each syllable and assign it a class of "symbol"
    let symbol = document.createElement('span');
    symbol.setAttribute('class', 'symbol');
    // if the user is promoted (i.e., has authority to scan previously un-scanned poems), show the previous scasion, symbol by symbol, in the cell above the word
    if (document.querySelector('#promoted') && document.querySelector('#promoted').textContent == 'Promoted: True') {
      symbol.textContent = `${scansion[k]}`;
    // otherwise, show a "u" (symbol of an unstressed syllable) for each syllable
    } else {
      symbol.textContent= 'u'
    }
    // add an event listener to each symbol that will toggle it between "/" and "u" when it is clicked
    symbol.addEventListener('click', (event) => {
      toggle(event);
    });
    // append the symbol to the cell
    scanCell.append(symbol);
    }
  if (window.innerWidth >= 600) {
    scanCell.addEventListener('mouseover', (event) => {
      showTooltip(event)
    })
    scanCell.addEventListener('mouseleave', hideTooltip)
  }
  // append this cell to the scansion row
  return scanCell;
}

function renderWordCell(word, lineNumber, wordNumber) {
  const wordCell = document.createElement('td');
  wordCell.setAttribute('id', `word${lineNumber}-${wordNumber}`);
  wordCell.setAttribute('class', 'word');
  wordCell.textContent = word;
  return wordCell;
}

function renderPlusMinusCell(lineNumber, wordNumber) {
  const plusMinusCell = document.createElement('td')
  plusMinusCell.setAttribute('id', `pm${lineNumber}-${wordNumber}`);
  plusMinusCell.setAttribute('class', 'pmc')
  
  // create a plus button
  let plus = document.createElement('button');
  plus.textContent = '+';
  plus.setAttribute('class', 'plus pm');
  
  // that when clicked calls a function that adds a syllable to the word
  plus.addEventListener('click', (event) => {
    addSyllable(event);
  });

  plusMinusCell.append(plus);
  
  // create a minus button
  let minus = document.createElement('button');
  minus.textContent = '-';
  minus.setAttribute('class', 'minus pm');

  // that when clicked calls a function that removes a syllable from the word
  minus.addEventListener('click', (event) => {
    removeSyllable(event);
  });

  // show tooltips if the screen is large enough
  if (window.innerWidth >= 600) {
    plusMinusCell.addEventListener('mouseover', (event) => {
      showTooltip(event);
    })
    plusMinusCell.addEventListener('mouseleave', hideTooltip);
  }

  plusMinusCell.append(minus);

  return plusMinusCell
}

// function to toggle a scansion syllable between stressed and unstressed (human users must
// commit to one or the other)
function toggle(event) {
  if (event.target.textContent === '/' || event.target.textContent === '?') {
    event.target.textContent = 'u';
  } else {
    event.target.textContent = '/';
  }
}

// function to add syllable to word
function addSyllable(event) {
  // get id of plusMinusCell
  let id = event.target.parentNode.id;
  // get suffix of id
  let suffix = id.slice(2)
  // get corresponding scansion cell
  let place = document.getElementById(`scansion${suffix}`)
  // add syllable with appropriate event listener (defaults to unstressed)
  let symbol = document.createElement('span');
  symbol.textContent = 'u';
  symbol.addEventListener('click', (event) => {
    toggle(event)
  });
  place.append(symbol);
}

// function to remove a syllable from a word
function removeSyllable(event) {
  let id = event.target.parentNode.id;
  let suffix = id.slice(2)
  let place = document.getElementById(`scansion${suffix}`)
  // find first syllable in cell;
  // do not attempt to remove symbols if there are none
  let symbol = place.querySelector('span');
  if (symbol) {
    symbol.remove();
  }
}

// function to submit new scansion or new score via a PUT request if user is logged in
function submitScansion() {
  // disable submit button so user can't increase score by resubmitting same scansion indefinitely
  // may eventually want to change it to giving feedback but still not affecting overall score
  document.querySelector('#submit-scansion').disabled = true;

  // get the original poem's scansion from hidden div in html and split it into lines
  const oldScansion = splitIntoLines(document.querySelector('#scansion-text').textContent);
  
  // make nested array for old scansion (an array of lines, each of which is an array of words); get word count for scoring later
  const oldScannedWords = []
  for (let i = 0; i < oldScansion.length; i++) {
    oldScannedWords.push(splitIntoWords(oldScansion[i]));
  }
  
  // get every table (i.e., every line of poetry or stanza-break line)
  const lines = document.querySelectorAll('table');
  
  // get the scansion from that line and create nested array a la oldScannedWords
  const newScannedWords = []
  for (let i = 0; i < lines.length; i++) {
    const newScansion = [];
    const scanCells = lines[i].querySelectorAll('.scansion');
    scanCells.forEach((cell) => {
      newScansion.push(cell.textContent);
    });
    newScannedWords.push(newScansion);
  }
  // get rounded percentage of words scanned differently
  const percentage = scoreScansion(oldScannedWords, newScannedWords);
  
  // this method from sources cited above the getCoookie function below
  csrftoken = getCookie();

  // if the user is promoted, submit the new scansion via a put request
  if (document.querySelector('#promoted') && document.querySelector('#promoted').textContent == 'Promoted: True') {
    poemId = document.getElementById('poem-id').textContent;
    alert(`New stresses will be recorded, but this will take a moment; disagreements between you and previous scansion (${percentage}% of words) will be marked in red, agreements in green.`)
    fetch('/', {method: 'PUT', body: JSON.stringify({
      scansion: stressPattern,
      id: poemId
    }), headers: { "X-CSRFToken": csrftoken },
    })
  // otherwise, calculate a score for the user
  } else {
    // score defaults to -1, which user will get if they get more than 0.3 of the words wrong.
    let score = -1;
    // if the user got fewer than a tenth of the words wrong, their score goes up by a point
    if (percentage < 10) {
      score = 1;
    // if the user got fewer than ~a third of the words wrong but more than
    // a tenth they're doing better than the computer, and have no impact
  } else if (percentage < 30) {
      score = 0;
    }
    // again, this method for getting csrf token verification is cited above
    // the getCookie function at the bottom
    // if the user is signed in, submit their score via a put request
    if (document.querySelector('#promoted')) {
      fetch('/', {method: 'PUT', body: JSON.stringify({
        score: score
      }), headers: { "X-CSRFToken": csrftoken },
      });
      oldScore = document.querySelector('#score')
      newScore = parseInt(oldScore.textContent, 10) + score;
      oldScore.textContent = newScore;
      // if new score is over 10, mark user as promoted and congratulate them;
      // updating their score in the database is taken care of in views.py
      if (newScore >= 10) {
        alert("You have graduated from training and are ready to help train the computer!")
        document.querySelector('#promoted').textContent = 'Promoted: True'
      }
      // if user is logged in, give them an alert about their score
      if (score == 1) {
        alert(`You have gained a point! Look at the poem to see where your scansion differed (${percentage}% of words) from the most recent authoritative scansion.`)
      } else if (score == -1) {
        alert(`You have lost a point! Look at the poem to see where your scansion differed (${percentage}% of words) from the most recent authoritative scansion.`)
      } else {
        alert(`You neither gained nor lost a point. Look at the poem to see where your scansion differed (${percentage}% of words) from the most recent authoritative scansion.`)
      }
    }
    // if not, tell them what their score would have been!
    if (!document.querySelector('#promoted')) {
      if (score == 1) {
        alert(`If you were logged in, you would have gained a point! Look at the poem to see where your scansion differed (${percentage}% of words) from the most recent authoritative scansion.`)
      } else if (score == -1) {
        alert(`If you were logged in, you would have lost a point! Look at the poem to see where your scansion differed (${percentage}% of words) from the most recent authoritative scansion.`)
      } else {
        alert(`If you were logged in, you would have neither gained nor lost a point. Look at the poem to see where your scansion differed (${percentage}% of words) from the most recent authoritative scansion.`)
      }
    }
  }
}

function showTooltip(event) {
  hideTooltip();
  const rect = event.target.getBoundingClientRect();
  const tX = rect.right + 50
  const tY = rect.top + 10 + window.pageYOffset
  let tooltip;
  if (event.target.className =="scansion" || event.target.className == "symbol") {
    tooltip = document.getElementById("sctooltip");
  } else {
    tooltip = document.getElementById("pmtooltip");
  }
  tooltip.style.left = `${tX}px`
  tooltip.style.top = `${tY}px`
  tooltip.style.visibility = 'visible';
}
function hideTooltip() {
  tooltips = document.querySelectorAll('.tooltip');
  console.log(tooltips);
  tooltips.forEach((element) => {
    element.style.visibility = 'hidden';
  })
}

function showControls(event) {
  // hide any other scansion open
  document.querySelectorAll('.pmc').forEach((element) => {
    element.style.display = 'none';
  });
  document.querySelectorAll('.scansion').forEach((element) => {
    element.style.display = 'none';
  })
  shrink();
  // get suffix of word's id and get corresponding scansion and plus-minus cells
  if (event.target.id) {
      const id = event.target.id;
      const suffix = id.slice(4);
      const scan = document.getElementById(`scansion${suffix}`);
      const pM = document.getElementById(`pm${suffix}`);
      event.target.style.fontSize = '30px';
      event.target.style.backgroundColor = 'lemonchiffon';
      // position those cells above and below the word respectively, guessing at pixel widths of elements
      // https://stackoverflow.com/questions/442404/retrieve-the-position-x-y-of-an-html-element-relative-to-the-browser-window
      // https://stackoverflow.com/questions/11373741/detecting-by-how-much-user-has-scrolled
      // https://stackoverflow.com/questions/38325789/getboundingclientrect-is-inaccurate
      const rect = event.target.getBoundingClientRect();
      const sX = (rect.left + rect.right) / 2 - scan.textContent.length * 10;
      const pMX = (rect.left + rect.right) / 2 - 20;
      const y = rect.top + window.pageYOffset;
      const pMY = rect.bottom + window.pageYOffset;
      scan.style.position = 'absolute';
      scan.style.left = `${sX}px`
      scan.style.top = `${y - 20}px`
      pM.style.position = 'absolute';
      pM.style.top = `${pMY}px`
      pM.style.left = `${pMX}px`;
      pM.style.backgroundColor = 'lemonchiffon';
      scan.style.display = 'inline';
      scan.childNodes.forEach((element) => {
        element.style.display = 'inline';
      })
      pM.style.display = 'inline';
    }
}
// found and adapted this function from Django documentation (as I'm only accessing one cookie,
// I figure I don't need to take cookie name as an argument, as the documentation does)
// https://stackoverflow.com/questions/43606056/proper-django-csrf-validation-using-fetch-post-request
// https://docs.djangoproject.com/en/1.11/ref/csrf/#how-to-use-it
function getCookie() {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim()
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, 'csrftoken'.length + 1) === ('csrftoken' + '=')) {
                cookieValue = decodeURIComponent(cookie.substring('csrftoken'.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
// cause word or word area clicked to increse font size of that word
// https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/String/search
// https://stackoverflow.com/questions/273789/is-there-a-version-of-javascripts-string-indexof-that-allows-for-regular-expr
// https://www.geeksforgeeks.org/javascript-regexp-d-metacharacter-2/#:~:text=The%20RegExp%20%5CD%20Metacharacter%20in,%5B%5E0%2D9%5D.&text=Example%201%3A%20This%20example%20searches,characters%20in%20the%20whole%20string.
function grow(elem) {
  // make all words normal size
  shrink();
  // get element's id
  id = elem.id;
  index = id.search(/\d/);
  hyphen = id.indexOf('-');
  if (!id || hyphen == -1 || index == -1) {
    id = elem.parentNode.id;
    index = id.search(/\d/);
    hyphen = id.indexOf('-');
    if (id && hyphen != -1 && index != -1) {
      suffix = id.slice(index);
      word = document.getElementById(`word${suffix}`);
      word.style.fontSize = '30px';
    }
  } else {
    suffix = id.slice(index);
    word = document.getElementById(`word${suffix}`);
    word.style.fontSize = '30px';
  }
}

// shrink all words to original size
function shrink() {
  document.querySelectorAll('.word').forEach((element) => {
    element.style.fontSize = '16px';
  });
}

function hideControls() {
  document.querySelectorAll('.pmc').forEach((element) => {
    element.style.display = 'none';
  })
  document.querySelectorAll('.scansion').forEach((element) => {
    element.style.display = 'none';
  })
}
function splitIntoLines(poemOrScansion) {
  return poemOrScansion.split(/\r\n|\n|\r/);
}

function splitIntoWords(line) {
  return line.trim().split(/\s+/)
}


function scoreScansion(oldScansionArr, newScansionArr) {
  const len = newScansionArr.length
  
  if (oldScansionArr.length != len) {
    console.log("mismatch in line lengths scoring");
  }

  // get a word count
  wordCount = 0
  for (let i = 0; i < len; i++) {
    wordCount += newScansionArr[i].length;
  }
  
  // let wordCount = document.querySelector('#scansion-text').textContent.split(' ').length;
 // create counter for differences
  let diffCounter = 0;
  // loop through lines of table
  for (let i = 0; i < len; i++) {
    lineLen = newScansionArr[i].length
    if (lineLen > 0) {
      for (let j = 0; j < lineLen; j++) {
        // if scansions are not the same, mark the cell pale red and increment the difference counter
        scanCell = document.getElementById(`scansion${i}-${j}`)
        wordCell = document.getElementById(`word${i}-${j}`)
        if (oldScansionArr[i][j] != newScansionArr[i][j]) {
          scanCell.style.backgroundColor = '#ffcccc';
          wordCell.style.backgroundColor = '#ffcccc';
          diffCounter++;
          // log what the difference should be; eventually this may be a tooltip
          console.log(`${newScansionArr[i][j]} should maybe be ${oldScansionArr[i][j]}; diffs = ${diffCounter}`);
          
          // if the scasions are the same, mark the cell pale green
        } else {
          scanCell.style.backgroundColor = '#99ffbb';
          wordCell.style.backgroundColor = '#99ffbb';
        }
      }
    }
  }
  return Math.round(diffCounter * 100 / wordCount)
}

// function to turn nested list of stresses into scansion string to be stored in database 
function makeScansionString(scansionArr) {
  const len = scansionArr.length;
  const stressPattern = []
  for (let i = 0; i < len; i++) {
    if (scansionArr[i]) {
      stressPattern.push(scansionArr[i].join(' ') + ' ');
    } else {
      stressPattern.push('\n')
    }
  }
  return stressPattern.join('\n')
}