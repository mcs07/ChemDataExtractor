# Contributing

Contributions of any kind are greatly appreciated!

## Feedback & Discussion

The [Issue Tracker](https://github.com/mcs07/ChemDataExtractor/issues) is the best place to post any feature ideas, 
requests and bug reports. This way, everyone has the opportunity to keep informed of changes and join the discussion on 
future plans.

## Contributing Code

If you are able to contribute changes yourself, just fork the [source code](https://github.com/mcs07/ChemDataExtractor) 
on GitHub, make changes and file a pull request. All contributions are welcome, no matter how big or small.

The following are especially welcome:

- New document readers for patent formats and the website HTML of scientific publishers.
- Improvements to NLP components - tokenization, tagging and entity recognition.
- Parsers for extracting new compound properties.
- New or improved documentation of existing features.

## Quick Guide to Contributing

1. [Fork the ChemDataExtractor repository on GitHub](https://github.com/mcs07/ChemDataExtractor/fork), then clone your 
   fork to your local machine:

        git clone https://github.com/<your-username>/ChemDataExtractor.git

2. Install the development requirements:

        cd ChemDataExtractor
        pip install -r requirements/development.txt

3. Create a new branch for your changes:

        git checkout -b <name-for-branch>

4. Make your changes or additions. Ideally add some tests and ensure they pass by running:

        pytest

   The output should show all tests passing.

5. Commit your changes and push to your fork on GitHub:

        git add .
        git commit -m "<description-of-changes>"
        git push origin <name-for-branch>

4. [Submit a pull request](https://github.com/mcs07/ChemDataExtractor/compare/). Then we can discuss your changes and
   merge them into the main ChemDataExtractor repository.

## Tips

- Follow the [PEP8](https://www.python.org/dev/peps/pep-0008) style guide.
- Include docstrings as described in [PEP257](https://www.python.org/dev/peps/pep-0257).
- Try and include tests that cover your changes.
- Try to write [good commit messages](http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html).
- Read the GitHub help page on [Using pull requests](https://help.github.com/articles/using-pull-requests).
