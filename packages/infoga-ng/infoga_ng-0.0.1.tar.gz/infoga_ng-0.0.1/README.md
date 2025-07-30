# Infoga-ng - Email OSINT

Infoga is a tool gathering email accounts informations (ip,hostname,country,...) from different public source (search engines, pgp key servers and shodan) and check if emails was leaked using haveibeenpwned.com API. Is a really simple tool, but very effective for the early stages of a penetration test or just to know the visibility of your company in the Internet.

![screen](https://raw.githubusercontent.com/mertcangokgoz/Infoga/master/screen/main.png)

It is a reorganized and packaged version of the infoga project for python3. Additional features may be added in the future.

## Installation

```bash
pip install infoga-ng
```

## This script is Tested in Ubuntu based OS

### Usage

```bash
infoga --domain nsa.gov --source all --breach -v 2 --report ../nsa_gov.txt
```

![run_1](https://raw.githubusercontent.com/mertcangokgoz/Infoga/master/screen/run_2.png)

```bash
infoga --info test@example.com --breach -v 3 --report ../example.txt
```

![info](https://raw.githubusercontent.com/mertcangokgoz/Infoga/master/screen/image_5.png)

## Docker Support

You can also run Infoga-ng using Docker. First, build the Docker image:

```bash
docker build -t infoga .
```

Then, run the container:

```bash
docker run --rm -it infoga --domain nsa.gov --source all --breach -v 2 --report /output/nsa_gov.txt
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
