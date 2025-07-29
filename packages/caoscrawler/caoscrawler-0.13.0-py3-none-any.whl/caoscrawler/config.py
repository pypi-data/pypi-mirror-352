# This file is a part of the CaosDB Project.
#
# Copyright (C) 2023 Indiscale GmbH <info@indiscale.com>
# Copyright (C) 2023 Henrik tom Wörden <h.tomwoerden@indiscale.com>
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
#

import linkahead as db

DEFAULTS = {
    "send_crawler_notifications": False,
    "create_crawler_status_records": False,
    "public_host_url": "/",
}


def get_config_setting(setting):
    caosdb_config = db.configuration.get_config()
    if "caoscrawler" in caosdb_config and setting in caosdb_config["caoscrawler"]:
        return caosdb_config["caoscrawler"][setting]
    else:
        return DEFAULTS[setting]
