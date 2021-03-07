
document.addEventListener('DOMContentLoaded', () => {
  // get poem and scansion from the HTML
  const poem = document.querySelector('#poem-text').textContent
  const scansion = document.querySelector('#scansion-text').textContent
  // return to normal size if something outside a word is clicked on, make the word if it or its controls are clicked on
  document.querySelector('.container').addEventListener('click', (event) => {
    grow(event.target);
  });
  // make dropdown menu work
  document.querySelector('#go').addEventListener('click', () => {
    let url = document.querySelector('#go-to-page').value
    if (url != 'none') {
            window.location = url;
        }
  })
  // split each into lines
  let lines = poem.split(/\r\n|\n|\r/);
  let scansion_lines = scansion.split(/\r\n|\n|\r/);
  // loop through the the lines
  for (let i = 0; i < lines.length; i++) {
    //remove any extra space from beginning and end of lines
    lines[i] = lines[i].trim()
    // if the line is not empty, start processing it
    if (lines[i]) {
      // split poem line on spaces (any number, though I've started manually eliminating leading space on poems)
      let words = lines[i].split(/\s+/);
      // remove leading and trailing from corresponding line of scansion and split it on spaces
      scansion_lines[i] = scansion_lines[i].trim()
      let scanned_words = scansion_lines[i].split(/\s+/);
      // create a table to hold each line
      let table = document.createElement('table');
      // identify it by its corresponding line
      table.setAttribute('id', `line${i}`);
      // create three rows in the table, one for stress patterns, one for words, and one for buttons to remove or add syllables
      table.innerHTML = `<tr class="stress-pattern"></tr>
                         <tr class="words"></tr>
                         <tr class="plus-minus"></tr>`;
      // append this table to the div intended for the poem to be scanned and assign each row to a variable
      document.querySelector('#poem-to-scan').append(table);
      let stress = table.querySelector(".stress-pattern");
      let wordRow = table.querySelector(".words");
      let plusMinus = table.querySelector(".plus-minus");
      // loop through the words in each line
      for (let j = 0; j < words.length; j++) {
        // for each word, create a cell and give it an id indicating where it falls and the purpose it serves
        let scansion = document.createElement('td');
        scansion.setAttribute('id', `scansion${i}-${j}`);
        scansion.setAttribute('class', 'scansion');
        // scansion.addEventListener('click', (event) => {
        //   grow(event.target)
        // });
        // append this cell to the scansion row
        stress.append(scansion);
        // if the scansion has a corresponding "word," add symbols to the cell to represent each syllable
        if (scanned_words[j]) {
          // loop through each syllable (indicated by a symbol) in the scansion
          for (let k = 0; k < scanned_words[j].length; k++) {
            // create a span for each syllable and assign it a class of "symbol"
            let symbol = document.createElement('span');
            symbol.setAttribute('class', 'symbol')
            // if the user is promoted (i.e., has authority to scan previously un-scanned poems), show the previous scasion, symbol by symbol, in the cell above the word
            if (document.querySelector('#promoted') && document.querySelector('#promoted').textContent == 'Promoted: True') {
              symbol.textContent = `${scanned_words[j][k]}`;
            // otherwise, show a "u" (symbol of an unstressed syllable) for each syllable
            } else {
              symbol.textContent= 'u'
            }
            // append the symbol to the cell
            scansion.append(symbol);
            // add an event listener to each symbol that will toggle it between "/" and "u" when it is clicked
            symbol.addEventListener('click', (event) => {
              toggle(event);
              // grow(event.target.parentNode);
            });
          }
        }
        // next, find the word corresponding to the scansion, create a table cell for it, add it to the cell, and append the cell to the row for words
        let word = document.createElement('td');
        word.setAttribute('id', `word${i}-${j}`);
        word.setAttribute('class', 'word');
        word.textContent = words[j];
        // word.addEventListener('click', (event) => {
        //   grow(event.target)
        // });
        // if this is a mobile device, add an event listener that will expand a given word's set of controls when that word is clicked
        // https://www.w3schools.com/howto/howto_js_media_queries.asp
        if (window.innerWidth <= 600) {
          word.addEventListener('click', (event) => {
            showControls(event);
          });
        }
        wordRow.append(word);
        // pronunciations change over time and between dialects, and the automated syllable makes mistakes as well; accordingly,
        // users should be able to add syllables to words or remove them; create a cell for plus and minus buttons, assign it the appropriate id and class, and append it to the third row of the table.
        let plusMinusCell = document.createElement('td')
        plusMinusCell.setAttribute('id', `pm${i}-${j}`);
        plusMinusCell.setAttribute('class', 'pmc')
        // plusMinusCell.addEventListener('click', (event) => {
        //   grow(event.target)
        // });
        plusMinus.append(plusMinusCell);
        // create a plus button
        let plus = document.createElement('button');
        plus.textContent = '+';
        plus.setAttribute('class', 'pm');
        // call a function that adds a syllable to the word when clicked
        plus.addEventListener('click', (event) => {
          addSyllable(event);
          // grow(event.target.parentNode)
        });
        plusMinusCell.append(plus);
        // create a minus button
        let minus = document.createElement('button');
        minus.textContent = '-';
        minus.setAttribute('class', 'pm');
        // call a function that removes a syllable from the word when clicked
        minus.addEventListener('click', (event) => {
          removeSyllable(event);
          // grow(event.target.parentNode);
        });
        plusMinusCell.append(minus);
      }
    // if the row is empty, insert an empty table for the stanza break
    } else {
      table = document.createElement('table');
      table.innerHTML = '<tr></tr><tr></tr>'
      table.setAttribute('class', 'empty')
      document.querySelector('#poem-to-scan').append(table);
    }
  }
  // add a submit button
  let button = document.createElement('button');
  button.setAttribute('id', 'submit-scansion');
  button.textContent = 'Scan Poem'
  button.addEventListener('click', submitScansion);
  document.querySelector('#poem-to-scan').append(button);

})
// toggle a scansion syllable between stressed and unstressed (human users must
// commit to one or the other)
function toggle(event) {
  if (event.target.textContent === '/' || event.target.textContent === '?') {
    event.target.textContent = 'u';
  } else {
    event.target.textContent = '/';
  }
}

// add syllable to word
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

// compare new scansion to old
// if appropriate, submit new scansion via a put request
function submitScansion() {
  // get every table containing a line of poetry
  const lines = document.querySelectorAll('table');
  // get the original poem's scansion from hidden div in html and split it into lines
  const oldScansion = document.querySelector('#scansion-text').textContent.split(/\r\n|\n|\r/);
  // get word count for scoring later
  let wordCount = document.querySelector('#scansion-text').textContent.split(' ').length;
  // disable submit button so user can't get points by submitting already-corrected work
  document.querySelector('#submit-scansion').disabled = true;
  // create empty string for stress pattern and counter for differences
  let stressPattern = '';
  let diffCounter = 0;
  // loop through lines of table
  for (let i = 0; i < lines.length; i++) {
    // get all cells containing words
    let words = lines[i].querySelectorAll('.word');
    // split corresponding line of original scansion into words
    let scannedWords = oldScansion[i].split(' ');
    // if table contains words, compare old scansion to new for each word
    if (words.length != 0) {
      for (let j = 0; j < words.length; j++) {
        // get id of each word and find the suffix
        id = words[j].id;
        suffix = id.slice(4);
        // get the scansion with the same suffix
        scanCell = document.getElementById(`scansion${suffix}`);
        // https://stackoverflow.com/questions/6967073/javascript-delete-all-occurrences-of-a-char-in-a-string
        // if the scansions are not the same, mark the cell pale red
        scansion = scanCell.textContent;
        console.log(scansion);
        if (scansion != scannedWords[j]) {
          scanCell.style.backgroundColor = '#ffcccc';
          words[j].style.backgroundColor = '#ffcccc';
          // log what the difference should be; eventually this may be a tooltip
          console.log(`${scansion} should maybe be ${scannedWords[j]}`)
          // increment the difference counter
          diffCounter++;
        // if the scasions are the same, mark the cell pale green
        } else {
          scanCell.style.backgroundColor = '#99ffbb';
          words[j].style.backgroundColor = '#99ffbb';
        }
        // add the new scansion plus a final space to the stress pattern
        stressPattern += `${scansion} `
        // if the word is the last in the line, add a newline
        if (j === words.length - 1)  {
          stressPattern += '\n'
        }
      }
      // if the line was empty, add a newline
    } else {
      stressPattern += '\n'
    }
  }
  // this method from sources cited above the getCoookie function below
  csrftoken = getCookie();
  // if the user is promoted, submit the new scansion via a put request
  if (document.querySelector('#promoted') && document.querySelector('#promoted').textContent == 'Promoted: True') {
    poemId = document.getElementById('poem-id').textContent;
    alert(`New stresses will be recorded, but this will take a moment; disagreements between you and previous scansion (${diffCounter / wordCount} of words) will be marked in red, agreements in green.`)
    fetch('/', {method: 'PUT', body: JSON.stringify({
      scansion: stressPattern,
      id: poemId
    }), headers: { "X-CSRFToken": csrftoken },
    })
  // otherwise, calculate a score for the user
  } else {
    const percentage = diffCounter / wordCount;
    // score defaults to -1, which user will get if they get more than 0.3 of the words wrong.
    let score = -1;
    // if the user got fewer than a tenth of the words wrong, their score goes up by a point
    if (percentage < 0.1) {
      score = 1;
    // if the user got fewer than ~a third of the words wrong but more than
    // a tenth they're doing better than the computer, and have no impact
    } else if (percentage < 0.3) {
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
        alert(`You have gained a point! Look at the poem to see where your scansion differed from the most recent authoritative scansion.`)
      } else if (score == -1) {
        alert(`You have lost a point! Look at the poem to see where your scansion differed from the most recent authoritative scansion.`)
      } else {
        alert(`You neither gained nor lost a point. Look at the poem to see where your scansion differed from the most recent authoritative scansion.`)
      }
    }
    // if not, tell them what their score would have been!
    if (!document.querySelector('#promoted')) {
      if (score == 1) {
        alert(`If you were logged in, you would have gained a point! Look at the poem to see where your scansion differed from the most recent authoritative scansion.`)
      } else if (score == -1) {
        alert(`If you were logged in, you would have lost a point! Look at the poem to see where your scansion differed from the most recent authoritative scansion.`)
      } else {
        alert(`If you were logged in, you would have neither gained nor lost a point. Look at the poem to see where your scansion differed from the most recent authoritative scansion.`)
      }
    }
  }
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
