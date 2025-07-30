/*
 * (C) Copyright 1996- ECMWF.
 *
 * This software is licensed under the terms of the Apache Licence Version 2.0
 * which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
 *
 * In applying this licence, ECMWF does not waive the privileges and immunities
 * granted to it by virtue of its status as an intergovernmental organisation nor
 * does it submit to any jurisdiction.
 */


#pragma once

#include "mir/mir_ecbuild_config.h"

#include "mir/api/mir_version.h"


#define mir_HAVE_ATLAS 1
#define mir_HAVE_ECKIT_GEO 1
#define mir_HAVE_NETCDF 0
#define mir_HAVE_PNG 0
#define mir_HAVE_OMP 0


constexpr bool _to_bool(int x = 0) {
    return x != 0;
}

constexpr bool HAVE_ATLAS     = _to_bool(1);
constexpr bool HAVE_ECKIT_GEO = _to_bool(1);
constexpr bool HAVE_NETCDF    = _to_bool(0);
constexpr bool HAVE_PNG       = _to_bool(0);
constexpr bool HAVE_OMP       = _to_bool(0);

constexpr bool HAVE_TESSELATION = _to_bool(1);
constexpr bool HAVE_PROJ        = _to_bool();
