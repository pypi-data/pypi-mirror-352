#!/usr/bin/env python3
# encoding: utf-8
#
# This file is a part of the CaosDB Project.
#
# Copyright (C) 2022 Henrik tom Wörden
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

import argparse

from caosadvancedtools.crawler import Crawler as OldCrawler


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("run_id",
                        help="Run ID or the crawler run that created the changes that shall be "
                        "authorized.")

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    OldCrawler.update_authorized_changes(args.run_id)
