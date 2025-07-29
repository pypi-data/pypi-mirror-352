/****************************************************************************
 * IFunctionImportProto.h
 *
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 *
 ****************************************************************************/
#pragma once
#include <stdint.h>
#include <unordered_map>
#include <memory>
#include <set>
#include <string>
#include <vector>
#include "zsp/ast/impl/UP.h"
#include "zsp/ast/IVisitor.h"
#include "zsp/ast/IFunctionImport.h"

namespace zsp {
namespace ast {

class IFunctionImport;
using IFunctionImportUP=UP<IFunctionImport>;
typedef std::shared_ptr<IFunctionImport> IFunctionImportSP;
class IFunctionPrototype;
using IFunctionPrototypeUP=UP<IFunctionPrototype>;
typedef std::shared_ptr<IFunctionPrototype> IFunctionPrototypeSP;
class IFunctionImportProto;
using IFunctionImportProtoUP=UP<IFunctionImportProto>;
class IFunctionImportProto : public virtual IFunctionImport {
public:
    
    virtual ~IFunctionImportProto() { }
    
    
    virtual IFunctionPrototype *getProto() const = 0;
    
    virtual void setProto(IFunctionPrototype *v, bool own=true) = 0;
};
    
    } // namespace zsp
    } // namespace ast
    
