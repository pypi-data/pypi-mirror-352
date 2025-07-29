#!/usr/bin/env python3
# encoding: utf-8
#
# This file is a part of the CaosDB Project.
#
# Copyright (C) 2023 Henrik tom Wörden <h.tomwoerden@indiscale.com>
# Copyright (C) 2023 IndiScale GmbH    <info@indiscale.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

import logging
import sys

from caosadvancedtools.serverside.helper import get_shared_filename
from caosadvancedtools.webui_formatter import WebUI_Formatter


def configure_server_side_logging(max_log_level: int = logging.INFO):
    """
    Set logging up to save one plain debugging log file, one plain info log
    file (for users) and a stdout stream with messages wrapped in html elements

    returns the path to the file with debugging output

    Parameters
    ----------
    max_log_level : int, optional
        The maximum log level to use for SSS-logs. Default is
        ``logging.INFO``.

    Returns
    -------
    userlog_public, htmluserlog_public, debuglog_public: str
        Public paths of the respective log files.
    """
    adv_logger = logging.getLogger("caosadvancedtools")
    # The max_<level> variables will be used to set the logger levels
    # to the respective maximum of intended level and max_log_level,
    # effectively cutting off logging above the specified
    # max_log_level.
    max_info = max(logging.INFO, max_log_level)
    max_debug = max(logging.DEBUG, max_log_level)
    adv_logger.setLevel(level=max_debug)

    cr_logger = logging.getLogger("caoscrawler")
    cr_logger.setLevel(level=max_debug)

    userlog_public, userlog_internal = get_shared_filename("userlog.txt")

    root_logger = logging.getLogger()
    root_logger.setLevel(level=max_info)

    # this is a log file with INFO level for the user
    user_file_handler = logging.FileHandler(filename=userlog_internal)
    user_file_handler.setLevel(logging.INFO)
    root_logger.addHandler(user_file_handler)

    # The output shall be printed in the webui. Thus wrap it in html elements.
    formatter = WebUI_Formatter(full_file="/Shared/{}".format(userlog_public))
    web_handler = logging.StreamHandler(stream=sys.stdout)
    web_handler.setFormatter(formatter)
    web_handler.setLevel(logging.INFO)
    root_logger.addHandler(web_handler)

    # Also create an HTML version for later use.
    htmluserlog_public, htmluserlog_internal = get_shared_filename("userlog.html")
    formatter = WebUI_Formatter(full_file="/Shared/{}".format(userlog_public))
    lweb_handler = logging.FileHandler(filename=htmluserlog_internal)
    lweb_handler.setFormatter(formatter)
    lweb_handler.setLevel(logging.INFO)
    root_logger.addHandler(lweb_handler)

    # one log file with debug level output
    debuglog_public, debuglog_internal = get_shared_filename("debuglog.txt")
    debug_handler = logging.FileHandler(filename=debuglog_internal)
    debug_handler.setLevel(logging.DEBUG)
    root_logger.addHandler(debug_handler)

    return userlog_public, htmluserlog_public, debuglog_public
