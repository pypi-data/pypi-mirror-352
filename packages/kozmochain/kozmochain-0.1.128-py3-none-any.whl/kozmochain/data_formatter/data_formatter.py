from importlib import import_module
from typing import Any, Optional

from kozmochain.chunkers.base_chunker import BaseChunker
from kozmochain.config import AddConfig
from kozmochain.config.add_config import ChunkerConfig, LoaderConfig
from kozmochain.helpers.json_serializable import JSONSerializable
from kozmochain.loaders.base_loader import BaseLoader
from kozmochain.models.data_type import DataType


class DataFormatter(JSONSerializable):
    """
    DataFormatter is an internal utility class which abstracts the mapping for
    loaders and chunkers to the data_type entered by the user in their
    .add or .add_local method call
    """

    def __init__(
        self,
        data_type: DataType,
        config: AddConfig,
        loader: Optional[BaseLoader] = None,
        chunker: Optional[BaseChunker] = None,
    ):
        """
        Initialize a dataformatter, set data type and chunker based on datatype.

        :param data_type: The type of the data to load and chunk.
        :type data_type: DataType
        :param config: AddConfig instance with nested loader and chunker config attributes.
        :type config: AddConfig
        """
        self.loader = self._get_loader(data_type=data_type, config=config.loader, loader=loader)
        self.chunker = self._get_chunker(data_type=data_type, config=config.chunker, chunker=chunker)

    @staticmethod
    def _lazy_load(module_path: str):
        module_path, class_name = module_path.rsplit(".", 1)
        module = import_module(module_path)
        return getattr(module, class_name)

    def _get_loader(
        self,
        data_type: DataType,
        config: LoaderConfig,
        loader: Optional[BaseLoader],
        **kwargs: Optional[dict[str, Any]],
    ) -> BaseLoader:
        """
        Returns the appropriate data loader for the given data type.

        :param data_type: The type of the data to load.
        :type data_type: DataType
        :param config: Config to initialize the loader with.
        :type config: LoaderConfig
        :raises ValueError: If an unsupported data type is provided.
        :return: The loader for the given data type.
        :rtype: BaseLoader
        """
        loaders = {
            DataType.YOUTUBE_VIDEO: "kozmochain.loaders.youtube_video.YoutubeVideoLoader",
            DataType.PDF_FILE: "kozmochain.loaders.pdf_file.PdfFileLoader",
            DataType.WEB_PAGE: "kozmochain.loaders.web_page.WebPageLoader",
            DataType.QNA_PAIR: "kozmochain.loaders.local_qna_pair.LocalQnaPairLoader",
            DataType.TEXT: "kozmochain.loaders.local_text.LocalTextLoader",
            DataType.DOCX: "kozmochain.loaders.docx_file.DocxFileLoader",
            DataType.SITEMAP: "kozmochain.loaders.sitemap.SitemapLoader",
            DataType.XML: "kozmochain.loaders.xml.XmlLoader",
            DataType.DOCS_SITE: "kozmochain.loaders.docs_site_loader.DocsSiteLoader",
            DataType.CSV: "kozmochain.loaders.csv.CsvLoader",
            DataType.MDX: "kozmochain.loaders.mdx.MdxLoader",
            DataType.IMAGE: "kozmochain.loaders.image.ImageLoader",
            DataType.UNSTRUCTURED: "kozmochain.loaders.unstructured_file.UnstructuredLoader",
            DataType.JSON: "kozmochain.loaders.json.JSONLoader",
            DataType.OPENAPI: "kozmochain.loaders.openapi.OpenAPILoader",
            DataType.GMAIL: "kozmochain.loaders.gmail.GmailLoader",
            DataType.NOTION: "kozmochain.loaders.notion.NotionLoader",
            DataType.SUBSTACK: "kozmochain.loaders.substack.SubstackLoader",
            DataType.YOUTUBE_CHANNEL: "kozmochain.loaders.youtube_channel.YoutubeChannelLoader",
            DataType.DISCORD: "kozmochain.loaders.discord.DiscordLoader",
            DataType.RSSFEED: "kozmochain.loaders.rss_feed.RSSFeedLoader",
            DataType.BEEHIIV: "kozmochain.loaders.beehiiv.BeehiivLoader",
            DataType.GOOGLE_DRIVE: "kozmochain.loaders.google_drive.GoogleDriveLoader",
            DataType.DIRECTORY: "kozmochain.loaders.directory_loader.DirectoryLoader",
            DataType.SLACK: "kozmochain.loaders.slack.SlackLoader",
            DataType.DROPBOX: "kozmochain.loaders.dropbox.DropboxLoader",
            DataType.TEXT_FILE: "kozmochain.loaders.text_file.TextFileLoader",
            DataType.EXCEL_FILE: "kozmochain.loaders.excel_file.ExcelFileLoader",
            DataType.AUDIO: "kozmochain.loaders.audio.AudioLoader",
        }

        if data_type == DataType.CUSTOM or loader is not None:
            loader_class: type = loader
            if loader_class:
                return loader_class
        elif data_type in loaders:
            loader_class: type = self._lazy_load(loaders[data_type])
            return loader_class()

        raise ValueError(
            f"Cant find the loader for {data_type}.\
                    We recommend to pass the loader to use data_type: {data_type},\
                        check `https://docs.digi-trans.org/data-sources/overview`."
        )

    def _get_chunker(self, data_type: DataType, config: ChunkerConfig, chunker: Optional[BaseChunker]) -> BaseChunker:
        """Returns the appropriate chunker for the given data type (updated for lazy loading)."""
        chunker_classes = {
            DataType.YOUTUBE_VIDEO: "kozmochain.chunkers.youtube_video.YoutubeVideoChunker",
            DataType.PDF_FILE: "kozmochain.chunkers.pdf_file.PdfFileChunker",
            DataType.WEB_PAGE: "kozmochain.chunkers.web_page.WebPageChunker",
            DataType.QNA_PAIR: "kozmochain.chunkers.qna_pair.QnaPairChunker",
            DataType.TEXT: "kozmochain.chunkers.text.TextChunker",
            DataType.DOCX: "kozmochain.chunkers.docx_file.DocxFileChunker",
            DataType.SITEMAP: "kozmochain.chunkers.sitemap.SitemapChunker",
            DataType.XML: "kozmochain.chunkers.xml.XmlChunker",
            DataType.DOCS_SITE: "kozmochain.chunkers.docs_site.DocsSiteChunker",
            DataType.CSV: "kozmochain.chunkers.table.TableChunker",
            DataType.MDX: "kozmochain.chunkers.mdx.MdxChunker",
            DataType.IMAGE: "kozmochain.chunkers.image.ImageChunker",
            DataType.UNSTRUCTURED: "kozmochain.chunkers.unstructured_file.UnstructuredFileChunker",
            DataType.JSON: "kozmochain.chunkers.json.JSONChunker",
            DataType.OPENAPI: "kozmochain.chunkers.openapi.OpenAPIChunker",
            DataType.GMAIL: "kozmochain.chunkers.gmail.GmailChunker",
            DataType.NOTION: "kozmochain.chunkers.notion.NotionChunker",
            DataType.SUBSTACK: "kozmochain.chunkers.substack.SubstackChunker",
            DataType.YOUTUBE_CHANNEL: "kozmochain.chunkers.common_chunker.CommonChunker",
            DataType.DISCORD: "kozmochain.chunkers.common_chunker.CommonChunker",
            DataType.CUSTOM: "kozmochain.chunkers.common_chunker.CommonChunker",
            DataType.RSSFEED: "kozmochain.chunkers.rss_feed.RSSFeedChunker",
            DataType.BEEHIIV: "kozmochain.chunkers.beehiiv.BeehiivChunker",
            DataType.GOOGLE_DRIVE: "kozmochain.chunkers.google_drive.GoogleDriveChunker",
            DataType.DIRECTORY: "kozmochain.chunkers.common_chunker.CommonChunker",
            DataType.SLACK: "kozmochain.chunkers.common_chunker.CommonChunker",
            DataType.DROPBOX: "kozmochain.chunkers.common_chunker.CommonChunker",
            DataType.TEXT_FILE: "kozmochain.chunkers.common_chunker.CommonChunker",
            DataType.EXCEL_FILE: "kozmochain.chunkers.excel_file.ExcelFileChunker",
            DataType.AUDIO: "kozmochain.chunkers.audio.AudioChunker",
        }

        if chunker is not None:
            return chunker
        elif data_type in chunker_classes:
            chunker_class = self._lazy_load(chunker_classes[data_type])
            chunker = chunker_class(config)
            chunker.set_data_type(data_type)
            return chunker

        raise ValueError(
            f"Cant find the chunker for {data_type}.\
                We recommend to pass the chunker to use data_type: {data_type},\
                    check `https://docs.digi-trans.org/data-sources/overview`."
        )
