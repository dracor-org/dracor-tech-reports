---
title: "Excursus: An Algorithmic Archaeology of a Living Corpus: GerDraCor as a Dynamic Epistemic Object"
label: d7-3-excursus-an-algorithmic-archaeology-of-a-living-corpus-gerdracor-as-a-dynamic-epistemic-object
---

While we have shown in section 3.2 that Git commits can be used as stable references to states of living corpora and thus as a mechanism for transparent versioning, in section 3.3 we explored in more detail which information about corpora and corpus files can be queried using the GitHub API. Our explorations in section 3.3 have also demonstrated that the use of Git not only provides a powerful versioning tool for CLS corpora, but that this use of the API generates a large amount of additional (technical) metadata about corpora. In the following excursus, we use this metadata for a more in-depth analysis of the genesis of a DraCor corpus (namely “GerDraCor”), taking the Git commit history as a basis.

The aim of this analysis is twofold: On the one hand, we want to use a particular example to demonstrate what it means that in CLS we are occasionally dealing with living corpora. On the other hand, we want to use the analysis to illustrate the power of Git-based versioning and the metadata generated in this process, not least against the background that this might also open up new research perspectives on the epistemic objects of CLS (now understood as technical objects). An executable (and thus fully reproducible) version of this analysis is accessible on GitHub. In addition, we are convinced that an in-depth knowledge of the constitution of a data set is necessary when wanting to repeat the research based on this data. If the data has changed in the meantime between the original research and the repeating research knowing what exactly changed in the data can help to understand possible deviations in results and allows that informed counter-measures can be taken.

As already mentioned, the “German Drama Corpus” (“GerDraCor”) will serve as our showcase. The corpus’ repository is available at

    https://github.com/dracor-org/gerdracor 

The first step in the analysis is downloading all the data on all GerDraCor commits from the repository on GitHub. Depending on the overall number of commits this can take a long time. In a previous attempt, fetching and preparing the data of GerDraCor from GitHub took 53min 29s. The following analysis will be based on data that was downloaded on February 14th, 2024. At the time of the download the GitHub Repository `“gerdracor” `contained 1492 commits. We consider each commit being an implicit version of a corpus and therefore we have 1492 versions of “German Drama Corpus” up to this date.

(d7-3-the-birth-of-gerdracor)=
### The “Birth” of GerDraCor

From the commit history of the repository of the German Drama Corpus we can retrieve the very first commit. This initial commit to the repository which is identified by the SHA value “`2f4e830a852960eba8e05d6b622b3bd64911ab6`9” was committed by Mathias Göbel (during a hackathon at the University of Potsdam) and dates from 2 December, 2016.

    https://github.com/dracor-org/gerdracor/commit/2f4e830a852960eba8e05d6b622b3bd64911ab69 

With this commit, 465 TEI-XML files were added to a data folder with the name `data`. The commit message “inital commit: converted text based on LINA and TextGrid” already reveals the initial source of the data of corpus: *LINA* is short for “Literary Network Analysis” and was the format developed in the project DLINA.[^18]

In the DLINA project, research on dramatic texts was based on derivatives of the full-texts taken from the TextGrid Repository[^19]. The “LINA files” included only metadata on the dramatic texts (e.g. date of publication) and very detailed structural information on the segmentation (acts, scenes); this included also information on which characters appear in which structural segment. Thus, the “Zwischenformat”[^20]-Files (i.e., files in an intermediary format) allowed for the extraction of networks based on the co-occurence of characters in the same structural segment (cf. Dario Kampkaspar, Trilcke 2015). The DLINA project officially released their corpus of 465 plays before the Digital Humanities DH2015 conference in Sydney. This corpus is also referred to as “Sydney Corpus” or the corpus with the “Codename Sydney”. Unlike the current practice in DraCor, DLINA used Git Tags[^21] on corpus data. In the GitHub Repository of the DLINA Corpus, there is a single tagged version `15.07-sydney`:

    https://github.com/dlina/project/releases/tag/15.07-sydney 

The respective commit

    https://github.com/dlina/project/commit/cca01b501a1a294772c2a6a9fe38944b930eea03 

adds a RelaxNG schema[^22] describing the “Zwischenformat”. Although this dates from August 31, 2016, this version number was already introduced more than a year before in a blog post dating from June 20, 2015. The blog post explains it as such:

> “The version number 15.07 is referring to ‘July 2015’ as we’re going to present our results at the DH2015 conference on July 2, 2015. Further versions of the DLINA Corpus will receive according versioning numbers.” (Fischer, Trilcke 2015)

The files in the first commit to the GerDraCor repository re-include the full text of the play from the TextGrid Repository source in the element `<text>`, but in the `<teiHeader>` contain the metadata of the LINA files. This metadata is transformed from the custom intermediary format (“Zwischenformat”) that was used in the DLINA project to an XML encoding following the Guidelines of the Text Encoding Initiative (TEI Guidelines).

(d7-3-a-living-corpus-growing)=
### A Living Corpus “Growing”

Fig. 3 shows the development of the number of plays included in the corpus versions of GerDraCor. It can be seen from the plot that in 2018 the corpus slowly begins to grow.

:::{figure} ./media/image8.png
Fig. 3 Development of the number of documents in all versions in GerDraCor
:::

Tab. 1 lists the number of plays being added per year from 2016 to 2024 which shows that from 2020 (the year the COVID19 pandemic began) onwards the number of plays added per year grows significantly.

| year | new | overall |
|:--------:|---------|-------------|
|   2016   | 465     | 465         |
|   2017   | 0       | 465         |
|   2018   | 7       | 472         |
|   2019   | 7       | 479         |
|   2020   | 41      | 520         |
|   2021   | 32      | 552         |
|   2022   | 45      | 597         |
|   2023   | 66      | 663         |
|   2024   | 15      | 678         |

*Tab. 1: Plays added to GerDraCor per year*

The “growth” of the corpus – to a certain extent – also results from diversifying the digital sources of which data is included.

Soon after the consolidation of the DLINA/TextGrid data the first Non-DLINA play was added. Corpus version “a0bf290a517092e3db27b5f37c30776f596565cd” dating from January 6, 2018 includes the play *Die Überschwemmung* by Franz Philipp Adolph Schouwärt[^23]. The play’s digital source data does not stem from the TextGrid Repository as in the case of the data from the DLINA project[^24], but is converted from Wikisource[^25]. The following plot Fig. 4 shows the distribution of sources used over time.

:::{figure} ./media/image4.png
Fig. 4: Development of the Distribution of the Digital Sources of GerDraCor
:::

In the course of its existence, the GerDraCor corpus also expands in terms of the time period covered (see Fig. 5).

:::{figure} ./media/image6.png
Fig. 5: Development of the time range (“YearNormalized”) covered by GerDraCor
:::

There is a second parameter that can be used to visualize the “growth” of a corpus – the sum of the file sizes of all TEI-XML documents in a corpus version. As expected, the overall size grows when adding plays to the corpus, but in 2017 it can also be observed that the overall size shrinks even though the number of plays stay the same. Still, plotting the size can be used to visualize changes when the overall number of documents stays the same, as happened in 2017, for example, when the total file sizes suddenly dropped. In this year no new plays were added to the corpus (see Tab. 1).

:::{figure} ./media/image10.png
Fig. 6: Development of the sum of all document sizes in all versions in GerDraCor
:::

We don't want to go into detail about what happened in 2017. What is more important to us at this moment is something else that clarifies our understanding of living corpora. Living corpora are not only characterized by the fact that the number of documents they contain is growing. Rather, it is also the case that the documents from living corpora themselves can change (e.g. grow or shrink), because they are enriched by additional mark-up or homogenized, which can lead, for example, to mark-up or metadata being deleted from the files (as was the case in 2017, to solve this cliffhanger).

Plotting the file size over a period of time is also useful to understand if and when a single file has been subject to modification. As an example we plot the file size of each version of the XML file of the play *Emilia Galotti* by Gotthold Ephraim Lessing[^26] in Fig. 7.

:::{figure} ./media/image7.png
Fig. 7: Development of file size of the play Emila Galotti over all versions in GerDraCor
:::

The change in color of the plotted line indicates the moment when the file was renamed from `1772-Lessing_Gotthold_Ephraim-Emilia_Galotti-lina.xml`[^27] to the still valid `lessing-emilia-galotti.xml`. In the initial version of the XML file the metadata in the `<teiHeader>` was based on the LINA file, but not in the format (“Zwischenformat”) that is available as `lina88` on the DLINA website[^28], but already encoded following the TEI Guidelines. The reference to DLINA is still kept in the TEI version in the `<publicationStmt>` encoded as an `<idno>` element until the version dated ‘12 May, 2019’ (see the section “Batch Edits as Major Revisions” below). A reference to the TextGrid source is contained in the `<sourceDesc>` and tagged as `<bibl type="digitalSource">` including a link to TextGrid in an `<idno>` element.[^29]

The full text content taken from TextGrid was included in the initial version in the `<text>` element without any line breaks and indentations on a single line only. The text is formatted in the third version (“`106fefd275c20c5b673a326e89647f7511ba9f76”`[^30]) which results in the steep increase of the file size. Overall, there are 26 versions in which the XML file of *Emilia Galotti* is modified.[^31]

(d7-3-batch-edits-as-major-revisions)=
### Batch Edits as Major Revisions

One can differentiate (at least) two major types of modifications to the files in a corpus version:

- Edits of single files only that bring a single file in shape;

- “Batch” edits that change all files at once.

The first edits need to be analyzed on an individual level. On a broader scale it must be said that these are, of course, relevant in reproduction studies because they might change, for example, the text resulting in different numbers of `<sp>`, stage direction, number of words, et cetera. We can always assume some effect on some of the metrics if there is a new version.[^32]

In the following, we identify and comment on the batch edits, because we assume that they introduce changes to the files that are the results of some automatic process, e.g. using element Y instead of X.

In the case of the very early GerDraCor there are two commits that introduce significant changes to where files are stored in the repository and how they are named:[^33]

- With the commit “e18c322706417825229f1471b15bd6daaeaf3ab1” dating from September 17, 2017 the folder containing the files is renamed from the initial `data` to `tei`.

- With the commit “fdac66ba90c2c094012dc90395e952411d324e4c”, on the same day, the file names of all TEI-XML files are changed to now match the identifier `playname`.[^34]

There are 11 versions in which all TEI files available at that time are modified at once. In the following we describe the relevant ones.

- The commit “7987eb78ecee670e999373d1917bf64b8b1e5253” dating from September 3, 2018 adds Wikidata identifiers to 468 of 468 TEI files available at that time. The identifier is included as an element `<idno>` with the value "`wikidata`" of the attribute `@type` in `<publicationStmt>.`

- The commit “e8b7285eb4adbecebbcfcf53046f9a1093f250762“ dating from October 16, 2018 changes the `<revisionDesc>` of 468 of 468 TEI files available at that time. This is a modification of all files that should not affect any metrics currently returned by the DraCor API.

- The commit “8145e178ee1714ac115d2097e7c6df8cd1181e91” dating from May 12, 2019 mainly changes several elements in the `<teiHeader>` of 472 of 472 TEI files available at that time.

With the initial version of GerDraCor the identifiers that were assigned to the TextGrid plays in the DLINA project were kept. These identifiers consisted of a running number that, in the case of the DLINA website, was prefixed with “`lina`”. In this version of the corpus these identifiers were replaced with DraCor Identifiers that include the corpus identifier, e.g. “`ger`” followed by a number with 6 digits. For example, in the case of the play *Emilia Galotti* the LINA identifier “88” or “`lina88`” as in the URL of the LINA on the DLINA Website becomes “`ger000088`”.

This implies that all the 465 Identifiers of the DLINA-based plays in GerDraCor can be “converted” into the DLINA identifiers by just stripping the leading zeros and, in the case of the URL of the DLINA website, pre-pending “`lina”` in the URL:

    https://dlina.github.io/linas/lina{XXX}

E.g. the DraCor identifier that is resolvable with the URL

    https://dracor.org/id/ger000010  

would result in

    https://dlina.github.io/linas/lina10

Vice versa

    https://dlina.github.io/linas/lina465   

would result in

    https://dracor.org/id/ger000465  

which is resolved to

    https://dracor.org/ger/immermann-das-gericht-von-st-petersburg

The remaining major revision commits are:

- The commit “e8c21cfd3b76bdcb05c6174e2c2d237d0d07c21e” dating from September 7, 2019 assigns a RelaxNG schema derived from the DraCor TEI ODD[^35] to 474 play TEI files available at that time.

- The commit “8f0b2ac84f85ebf79df6b8aa0fb2d9662ee212ea” dating from January 16, 2020 changes the values of the attribute `@xml:lang` of the root element \<`TEI`\> from ISO-639-1 to ISO-639-2 codes, e.g. from "`de`" to "`ger`" in all 480 play TEI files available at that time.

- The commit “9c2fcf55cce2ec6290ffc8615e98d9b2355707d9” dating from December 5, 2020 introduces the following modifications to all 510 TEI files available at that time:

  - date ranges, e.g. of the date of first publication of a play, are encoded using the attributes `@notBefore` and `@notAfter`, e.g. a previous encoded time span as in `<date type="written" when="1885">1884–1885</date>` becomes `<date type="written" notBefore="1884" notAfter="1885">1884–1885</date>`.

  - The diverse genre terms encoded as element `<term>` in `<keywords>` in the `<textClass>` section of the header that have been available in previous versions, e.g. `<term type="genreTitle">Schattenspiel</term>`, `<term type="genreTitle">Studentenspiel</term>` are either removed (resulting in `<term type="genreTitle"/>`) or normalized, e.g. the German \<`term type="genreTitle">Komödie</term>` becomes `<term type="genreTitle">Comedy</term>`.

  - In addition to the normalized genre terms genre information is encoded using the element `<classCode>` in `<textClass>` linking to some selected concepts on Wikidata, e.g. `<classCode scheme="http://www.wikidata.org/entity/">Q40831</classCode>`. In this case the Wikidata identifier (Q-Number) identifies the concept “Comedy” ([Q40831](https://www.wikidata.org/wiki/Q40831)[^36]) on Wikidata.[^37]

- The commit “75b663876d1cd7b54235547ccd077a3299877a1c” dating from May 16, 2022 introduces a new element \<`standOff`\> to hold context metadata to all 569 TEI files available at that time.[^38]

  - The wikidata identifier, previously encoded as element `<idno>`, is included in `<standOff>` as an element `<link>` with the value "`wikidata`" of the `@type` attribute and linking to the corresponding entity on Wikidata by including the concept URI in the `@target` attribute.

  - The dates (printed, written, premiered) are also moved to the `<standOff>` container and are encoded as a `<listEvent>` with typed `<event> `elements.

- The commit “d23a93d9fa0e4eb53a580904ac5d01c8b8f8037c” dating from June 3, 2022 adds the DraCor ID as the value of the attribute `@xml:id` to the root element `<TEI>` and changes the encoding of the reference to Wikidata from a `<link>` to a `<relation>` with the value "`wikidata`" of the attribute `@type` to all 569 TEI files available at that time.

In this systematic perspective that is based on commits that change all files included in a corpus version at a time, we might still miss some important milestones in the development of the corpus if the respective changes in the encoding are not introduced at once but bit by bit to one or several files. For example, this is the case when introducing a new “feature”, the encoding of social or family relations of characters.[^39] This feature was introduced to GerDraCor in cooperation with the “QuaDramA” project (Wiedmer, Pagel, Reiter 2020).[^40] The elements `<relation>` in a `<listRelation type="personal"> `in the `<teiHeader>` were added between September and November 2019 to 358 GerDraCor files.

What we have shown in this excursus was just a small example of the possibilities that a corpus archaeology can offer based on the information that the GitHub API makes available as the commit history. With the excursus, we wanted to illustrate how important it is from our perspective to familiarize oneself as comprehensively as possible with the epistemic objects of one's own research, i.e. –- in the case of CLS research — to gain a deep understanding of the origin, genesis and development of a corpus.

[^18]: The project members included Frank Fischer, Mathias Göbel, Dario Kampkaspar, Christopher Kittel and Peer Trilcke. The output of the project is well documented on the project’s Blog (<https://dlina.github.io/>), the data and tools are available on GitHub at dlina (<https://github.com/dlina>). The term LINA as an abbreviation of the German “Literarische Netzwerkanalyse” (Literary Network Analysis) first appeared in print in the publication Trilcke 2013.
[^19]: <https://textgridrep.org>
[^20]: <https://dlina.github.io/Introducing-Our-Zwischenformat>
[^21]: <https://git-scm.com/docs/gitglossary#Documentation/gitglossary.txt-aiddeftagatag>, see also https://git-scm.com/book/en/v2/Git-Basics-Tagging
[^22]: RELAX NG Specification. Ed. by James Clark, Murata Makoto. 3 December 2001. OASIS Committee Specification. <https://www.oasis-open.org/committees/relax-ng/spec-20011203.html>.
[^23]: The identifier playname of the play is schouwaert-die-ueberschwemmung. The play can be accessed on the production instance of DraCor at <https://dracor.org/id/ger000466>.
[^24]: In a blog post (<https://dlina.github.io/A-Not-So-Simple-Question>) Fischer and Göbel \[2015\] conducted an evaluation of the data set “Digitale Bibliothek” (<https://www.textgrid.de/Digitale-Bibliothek>) that is included in TextGrid with the aim of identifying all available plays. The extracted TEI files can be found in this repository GitHub repository: <https://github.com/DLiNa/project/tree/master/data/textgrid-repository-dramas>
[^25]: <https://de.wikisource.org/wiki/Schouw%C3%A4rt_%E2%80%93_Die_Ueberschwemmung_(1784)>
[^26]: The play can be accessed on DraCor at <https://dracor.org/id/ger000088>.
[^27]: See the file on GitHub: <https://github.com/dracor-org/gerdracor/blob/2f4e830a852960eba8e05d6b622b3bd64911ab69/data/1772-Lessing_Gotthold_Ephraim-Emilia_Galotti-lina.xml>
[^28]: <https://dlina.github.io/linas/lina88/>
[^29]: <http://www.textgridrep.org/textgrid:rksp.0>
[^30]: <https://github.com/dracor-org/gerdracor/commit/106fefd275c20c5b673a326e89647f7511ba9f76#diff-0d89c2bc1b36f1ca71e870eeb075d3f23d463ac76716a6709d7b7d8705adff6e>
[^31]: The the identifiers of the versions in which the file is modified are as follows:

    \[‘3e92970c6c3901b7661a515ce504605fb819e37d’, ‘5d4130230eb9b9f2820618089ed1cf774424f241’, ‘51dd69475f14757992c77d9a04c19026295b5f7c’, ‘5b41d0f8f11fa478cfa68f9dac54912e6b922a63’, ‘7987eb78ecee670e999373d1917bf64b8b1e5253’, ‘e8b7285eb4adbecebbcfcf53046f9a1093f25076’, ‘879250ad0d9cc686dda930afa694d9461a0b5757’, ‘8145e178ee1714ac115d2097e7c6df8cd1181e91’, ‘1ab8c9b713a3eeaf5b25026e6036caaab230c119’, ‘e8c21cfd3b76bdcb05c6174e2c2d237d0d07c21e’, ‘23833340aa83b963205f583189206a9881e9869e’, ‘d71e3d78562d8039f90bd21d88c6c7b67e912372’, ‘b0c6457ed5233ca634650d853627ed4ffe5fba8a’, ‘e1622273f41204a09d9af469d8f036a79b654af9’, ‘1095d70934ab525f866a2f1978541eeedf618651’, ‘8f0b2ac84f85ebf79df6b8aa0fb2d9662ee212ea’, ‘9c2fcf55cce2ec6290ffc8615e98d9b2355707d9’, ‘445a5b0fca0c96d7d4be7a9e8738a7c19cbe9cad’, ‘7b4faf2f0d6e80a7e39052a38e12617453a1e5d2’, ‘75b663876d1cd7b54235547ccd077a3299877a1c’, ‘fe53f8f5d4d36794df55859e262e6d1b893ce705’, ‘d23a93d9fa0e4eb53a580904ac5d01c8b8f8037c’, ‘376cec4c609bc27cdcd9e2bb41bda7253c0174ff’, ‘bfadf6b5844d4e05ea0501898a23c21f71c10cb3’, ‘f7af1eb1060e94a916b856596d9e2e198f7159ea’, ‘a99060f0065856f8df114ce8556c31161c0332d1’\].
[^32]: There might be commits/versions in which only non-(play)-document files changed; usually these are unproblematic because these modifications do not affect the metrics and data returned by the API or any parts of files that are normally subject to an analysis, like the full text.
[^33]: With the current setup of the the methods provided by our analysis tool github_utils (see section 3.3) it is necessary to take changes in file names into consideration if we want to investigate or visualize the changes of a file over the whole period. After the batch renaming in September 2017 the data folder name tei stays stable, but there is still some renaming happening. The method get_ids_of_corpus_versions_renaming_documents allows to retrieve the idendifiers of all versions in which document files are renamed. The method get_renamed_files returns dictionaries containing the version number as well as the old and the new filename. The following plays have been renamed after the above mentioned batch renaming: \[‘goethe-faust-eine-tragoedie’, ‘malss-die-jungfern-koechinnen’, ‘neuber-die-beschuetzte-schauspielkunst’, ‘neuber-die-verehrung-der-vollkommenheit’, ‘lortzing-der-wildschuetz’, ‘schlegel-alarcos’, ‘hauptmann-die-ratten’, ‘hauptmann-florian-geyer’, ‘hauptmann-gabriel-schillings-flucht’, ‘hauptmann-vor-sonnenaufgang’, ‘holz-jerschke-traumulus’, ‘holz-schlaf-die-familie-selicke’, ‘laufs-jacoby-pension-schoeller’, ‘seemann-dulk-die-waende’, ‘stephanie-der-schauspieldirektor’, ‘stephanie-die-entfuehrung-aus-dem-serail’, ‘stephanie-die-liebe-im-narrenhause’, ‘stephanie-doktor-und-apotheker’, ‘barlach-der-blaue-boll’\].
[^34]: In the report “On Programmable Corpora” (Börner, Trilcke 2023) this is the feature “P3 play_name”, see “Tab. 02: Play Features” (Börner, Trilcke 2023: 38). This identifier is used, for example, when requesting information about the play from the API: <https://dracor.org/api/v1/corpora/ger/plays/lessing-emilia-galotti>; Documentation of this API endpoint see <https://dracor.org/doc/api#/public/play-info>.
[^35]: ODD and schema can be found in the GitHub repository <https://github.com/dracor-org/dracor-schema>. When using the ODD derived schema to validate TEI-XML files of corpus versions of the past it would be necessary to also use the respective version of the schema, which would need to be retrieved from the commit history of the schema repository. It would make changes in the encoding more transparent if, at least for schemas or ODD, some sort of explicit version numbers would be used that could be then referenced in the TEI files of the plays. The TEI Guidelines define an attribute \@version (<https://www.tei-c.org/release/doc/tei-p5-doc/en/html/ref-TEI.html#tei_att.version>) which “specifies *the version number of the TEI Guidelines* \[our emphasis\] against which this document is valid”. Strictly speaking, in the proposed use case the attribute would not point to an “official” TEI release but to a versioned ODD or \<schemaSpec\>element. This might be considered tag abuse and has still to be evaluated.
[^36]: <https://www.wikidata.org/wiki/Q40831>
[^37]: For the discussion of this encoding strategy and its implementation in the API see also the corresponding issue in the DraCor API repository: <https://github.com/dracor-org/dracor-api/issues/120> (opened 3 December, 2020) which exemplifies the interdependence of API code and TEI-Encoding of the DraCor corpora. The class codes are the basis for the extractor mechanism which allows to include genre information in the API responses, see feature “P22 play_genre_normalized” in “Tab. 02: Play features” in the report “On Programmable Corpora” (Börner, Trilcke 2023: 38). Class codes that are supported are hard coded in the API code, e.g. <https://github.com/dracor-org/dracor-api/blob/665ea3f07c3f0ab83566440436691ed73957b263/modules/config.xqm#L79-L89>.
[^38]: The introduction of the \<standOff\> element is discussed in this issue in the DraCor schema repository: <https://github.com/dracor-org/dracor-schema/issues/38> (the issue was opened on 14 March and closed on 2 July, 2022). This change of encoding is also a good example of the implications for other projects using DraCor corpora in their research: GerDraCor is used in several research projects, amongst them “QuaDramA” (<https://quadrama.github.io/>). In this project, two libraries were developed: “DramaNLP” (<https://github.com/quadrama/DramaNLP>) and “DramaAnalysis” (<https://github.com/quadrama/DramaAnalysis>). “DramaNLP” is the tool that generates the data to be analyzed with the R library “DramaAnalysis”. The changes introduced in the GerDraCor version discussed above had to be incorporated into DramaNLP as well, see the respective commit dating from 13 December, 2022 (<https://github.com/quadrama/DramaNLP/issues/97>).
[^39]: Regarding the feature and its implementation in DraCor services, see the report “On Programmable Corpora” (Börner, Trilcke 2023: 48–49, 62).
[^40]: The pull request that included the data into DraCor dates from November 24, 2019: <https://github.com/dracor-org/gerdracor/pull/10>
