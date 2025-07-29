/****************************************************************************
 * IStruct.h
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
#include "zsp/ast/ITypeScope.h"

#include "zsp/ast/StructKind.h"
namespace zsp {
namespace ast {

class ITypeScope;
using ITypeScopeUP=UP<ITypeScope>;
typedef std::shared_ptr<ITypeScope> ITypeScopeSP;
class IStruct;
using IStructUP=UP<IStruct>;
class IStruct : public virtual ITypeScope {
public:
    
    virtual ~IStruct() { }
    
    
    virtual StructKind getKind() const = 0;
    
    virtual void setKind(StructKind v) = 0;
};
    
    } // namespace zsp
    } // namespace ast
    
