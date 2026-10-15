# Codex PDF to EPUB

Use Codex to convert PDFs to EPUBs, complete with an instruction set containing extensive generalisable corrections, including incorrect punctuation marks, line breaks, italicisation, bolding, and so on. Simply clone this repo, pull in the source PDF, run `codex`, and tell it to convert it to an EPUB, and it will automatically read the extensive instructions in [AGENTS.md](https://github.com/JakeHPark/Codex-PDF-to-EPUB/blob/main/AGENTS.md) to overcome most common (and some uncommon) pitfalls. It will also automatically update its own instructions when it decides any solutions it comes up with or any corrections you specify are generalisable to future conversions.

- You should always try to source the cleanest, best-quality PDFs you can. Reasonably clean book scans are okay. [Here](https://media.githubusercontent.com/media/JakeHPark/Codex-PDF-to-EPUB/refs/heads/examples/You%20Can%20Be%20Right%20-%20Dana%20Adam%20Shapiro.epub) is the EPUB generated from *[You Can Be Right (or You Can Be Married)](https://www.amazon.com/You-Can-Be-Right-Married/dp/1451657781)* from a reasonably clean book scan. You can find the source PDF (and my EPUB) on [Anna's Archive](https://en.wikipedia.org/wiki/Anna's_Archive).
- This also works for books and essays that have been made available online in HTML, in which case you can just use a URL as the source. [Here](https://media.githubusercontent.com/media/JakeHPark/Codex-PDF-to-EPUB/refs/heads/examples/The%20Story%20of%20Zoya%20and%20Shura%20-%20L%20Kosmodemyanskaya.epub) is the EPUB generated from *[The Story of Zoya and Shura](https://gammacloud.org/features/zoya/story-zoya-shura/)* in this fashion.
- Wherever possible, you should first see if there already is a good EPUB option available: many academic journals permit you to download articles in EPUB format. Then you can smooth out the rough edges: if there's no cover, you can generate one; if there's residual errors, you can correct them. [Here](https://media.githubusercontent.com/media/JakeHPark/Codex-PDF-to-EPUB/refs/heads/examples/The%20experience%20of%20drowning%20-%20Michael%20Tipton%2C%20Hugh%20Montgomery.epub) is the cleaned-up EPUB generated from the EPUB of *[The experience of drowning](https://journals.sagepub.com/doi/10.1177/00258172211053127)* on Sage Journals.
- Tables, graphs, diagrams, images, and mathematical equations can all be converted neatly, but only if they are sequenced in a relatively linear, clear-cut fashion. [Here](https://media.githubusercontent.com/media/JakeHPark/Codex-PDF-to-EPUB/refs/heads/examples/What%20Predicts%20Divorce%20-%20John%20Mordechai%20Gottman.epub) is the EPUB generated from a clean, mostly plaintext-based PDF of *[What Predicts Divorce](https://www.amazon.com/What-Predicts-Divorce-Relationship-Processes/dp/0805814027)*, containing plenty of tables and statistics. You can find the source PDF (and my EPUB) on [Anna's Archive](https://en.wikipedia.org/wiki/Anna's_Archive).
- Sometimes, a useful but imperfect transcription is available alongside a more authoritative source. For example, you may have a good EPUB of an older edition of a book, and a scanned PDF of a newer edition. Alternatively, you may have an imperfect cleaned-up OCR PDF plus a more authoritative scanned PDF source. In such instances, you can provide both for a more reliable conversion. [Here](https://media.githubusercontent.com/media/JakeHPark/Codex-PDF-to-EPUB/refs/heads/examples/Ukraine%20and%20Russia%20-%20Paul%20D%27Anieri.epub) is the EPUB generated from *[Ukraine and Russia](https://www.cambridge.org/core/books/ukraine-and-russia/EE1BF8E4D463FBACD0CCEF52A7B1CF69)* from an excellent EPUB of an older edition combined with an authoritative PDF of a newer edition, both of which you can find on [Anna's Archive](https://en.wikipedia.org/wiki/Anna's_Archive) (my new EPUB is also there).
- Certain books that are heavily dependent on formatting and imagery, such as textbooks or books on fashion, may require much more book-specific instructions, or even not be worth converting. A little bit of creativity goes a long way! [Here](https://media.githubusercontent.com/media/JakeHPark/Codex-PDF-to-EPUB/refs/heads/examples/Postural%20Disorders%20and%20Musculoskeletal%20Dysfunction%20-%20Gill%20Solberg.epub) is the EPUB generated from *[Postural Disorders and Musculoskeletal Dysfunction](https://www.amazon.com/Postural-Disorders-Musculoskeletal-Dysfunction-Prevention/dp/0443103828)*, a textbook with lots of images, diagrams and notes in all sorts of places—left, right and centre.
- I like to use the Sol variant of GPT on the Medium mode as a good balance between cost and efficacy.

## Examples

The example EPUBs live on a [separate branch](https://github.com/JakeHPark/Codex-PDF-to-EPUB/tree/examples), stored with Git LFS. The local `examples/` directory is ignored by the main branch and can be checked out separately:

```sh
git fetch origin examples
git worktree add -b examples examples origin/examples
git -C examples lfs pull
```

If the local `examples` branch already exists, use `git worktree add examples examples` for the second command.

## Example prompt

It is important to convey the most important book-specific constraints concisely and explicitly. Here is an example of a good instruction:

> Okay, I want to continue stress-testing you to hone your instruction set. *The Anatomical Venus* by Joanna Ebenstein is next. I expect you to extract the images as they are in original quality and embed them losslessly into the EPUB. There are sidebars, which you now hopefully know to deal with; lots of full-page images, which you can extract with something like `pdfimages`; and some full pages of stylised text like on PDF page 40, which you can just extract as images rather than try to OCR and lose the aesthetic grandeur. Once you figure out how to do the first few pages it's actually quite repetitive: very clean text, more sidebars, more inline images, and more full-page images. The images on PDF pages 5+6, 9+10, 11+12, 15+16, 23+24, 31+32, 33+34, 35+36, 57+58, 63+64, 65+66, 69+70, 87+88, 91+92, 95+96, 99+100, 103+104, 107+108, 111+112, 121+122, 167+168, 169+170, 177+178, 199+200, 215+216, need to be joined horizontally, as the images were expected to be viewed continuously from the left to right page. Also, separately create an output ZIP containing all the original-quality images in the book, with the left-right pairs stitched together.

The original pass took 55 minutes using GPT-6.1 Sol, then I had to apply these book-specific corrections, which took another 48 minutes:

> > fig.1 The most iconic dissectible wax Anatomical Venus— also known as the ‘Demountable Venus’ and the ‘Medici Venus’— from the workshop of Clemente Susini at La Specola, Florence, Italy (1780-82). Life-sized.
>
> In the PDF, the em-dashes are followed by line breaks, so I understand your mistake here; regardless, there shouldn't be spaces after. It should also be "fig. 1" with a single space, not zero or two spaces. Also, "fig. 1" is duplicated in the above image; can you crop out just the photo? Make sure cropped images don't include any unnecessary surrounding blank space, whether it be white, grey or black. Generalise these corrections to the rest of the book, too.
>
> > The *Anatomical* Venus begins at the time and place of the creation of the Medici Venus
>
> *The Anatomical Venus* should be italicised in its entirety.
>
> > fig. 2 Early-eighteenthcentury dissectible ivory miniature manikin of a pregnant female, Italy.
>
> Should be "Early-eighteenth-century". It seems like you've applied the usually correct heuristic that hyphens at the ends of lines in PDFs should be removed in the EPUB, but this doesn't apply when the hyphens are actually part of the syntax. Also, this is in the wrong place: both fig. 2 and fig. 3 have been grouped in the same image. Generalise these corrections to the rest of the book.
>
> > *PREVIOUS*
> >
> > *page 20 Detail of a wax model in the ninth month of pregnancy. From the workshop of Gustav Zeiller, Berlin, Germany (c. 1880).*
> >
> > *pages 22-23 The Medici Venus (1780-82), displayed intact and dissected.*
>
> Well done on the excellent OCR, but headings like "PREVIOUS" and "OVERLEAF" and the page numbers no longer make sense in the EPUB.
>
> > *Taken from Anatomie des parties de la génération de l'homme et de la femme (1773) (left page, both; right page, right side) and Anatomie generale des visceres en situation (1772) (right page, left side).*
>
> Replace "left page" and "right page" with "above" and "below" respectively.

Some of these corrections may no longer need to be applied explicitly from now on, since they have been incorporated into the instruction set. [Here](https://media.githubusercontent.com/media/JakeHPark/Codex-PDF-to-EPUB/refs/heads/examples/The%20Anatomical%20Venus%20-%20Joanna%20Ebenstein.epub) is the resulting EPUB.

AI prompt engineering is a legitimate skill requiring a surprising amount of persistence, ingenuity and practice. I am not interested in trying to eliminate every minor error; I specifically look for high-leverage corrections like this that can be repeated across the book and other similar books. This is the *[Pareto principle](https://en.wikipedia.org/wiki/Pareto_principle)*: 80% of the benefit comes from 20% of the most worthwhile fixes. [Perfection is the enemy of good](https://en.wikipedia.org/wiki/Perfect_is_the_enemy_of_good): at the point of [diminishing functional returns](https://en.wikipedia.org/wiki/Diminishing_returns), *[opportunity cost](https://en.wikipedia.org/wiki/Opportunity_cost)* dictates that we must move on to the next project. This is called *[satisficing](https://en.wikipedia.org/wiki/Satisficing)*: making a choice that suffices to fill the most important requirements so that you can move on with your life. This doesn't mean we abandon our high standards; it simply means we gain more from tackling something else using the lessons we've learned. This is why teachers get their students to move on to the next subject even though their understanding of the current one is mediocre, or why a physical trainer or music teacher might teach you a new exercise even though you're still visibly imperfect on the old one. **Deliver a functional output, then try to do better next time.**
