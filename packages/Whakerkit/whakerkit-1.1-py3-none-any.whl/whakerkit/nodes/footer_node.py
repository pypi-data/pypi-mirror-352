# -*- coding: UTF-8 -*-
"""
:filename: whakerkit.nodes.footer_node.py
:author: Brigitte Bigi
:contributor: Chiheb Bradai
:contact: contact@sppas.org
:summary: HTMLNode for the footer

Copyright (C) 2024-2025 Brigitte Bigi, CNRS
Laboratoire Parole et Langage, Aix-en-Provence, France

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

This banner notice must not be removed.

"""

import os

from whakerpy.htmlmaker import HTMLNode
from whakerpy.htmlmaker import HTMLFooterNode

import whakerkit
from whakerkit import _

# ---------------------------------------------------------------------------


MSG_POWERED_BY = _("Powered by WhakerKit")

# ---------------------------------------------------------------------------


class WhakerKitFooterNode(HTMLFooterNode):
    """Node for the footer.

    """

    def __init__(self, parent: str):
        """Create the footer node.

        :param parent: (str) The parent node identifier

        """
        super(WhakerKitFooterNode, self).__init__(parent)
        self.reset()
        self.set_attribute("id", "footer-content")

    def reset(self):
        """Reset the footer to its default values.

        """
        # Delete the existing list of children
        self._children = list()
        footer_filename = whakerkit.sg.base_dir + "/html/footer.htm"
        if os.path.exists(footer_filename) is True:
            with open(footer_filename, encoding="utf-8") as html_file:
                self.set_value(html_file.read())

        self.append_child(HTMLNode(self.identifier, None, "hr"))

        content = ('<a href="https://whakerkit.sourceforge.io">'
                   f'   <img style="width: 1rem;" src="{whakerkit.sg.path}statics/icons/favicon.ico" alt="(W) ">'
                   '</a> '
                   f'<p><small>{MSG_POWERED_BY}<small></p>'
                   )
        power = HTMLNode(self.identifier, None, "section",
                         value=content,
                         attributes={"class": "center"})
        self.append_child(power)
