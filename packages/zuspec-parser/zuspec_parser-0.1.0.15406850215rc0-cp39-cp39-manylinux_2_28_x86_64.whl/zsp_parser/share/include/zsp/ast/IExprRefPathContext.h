/****************************************************************************
 * IExprRefPathContext.h
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
#include "zsp/ast/IExprRefPath.h"

namespace zsp {
namespace ast {

class IExprRefPath;
using IExprRefPathUP=UP<IExprRefPath>;
typedef std::shared_ptr<IExprRefPath> IExprRefPathSP;
class IExprHierarchicalId;
using IExprHierarchicalIdUP=UP<IExprHierarchicalId>;
typedef std::shared_ptr<IExprHierarchicalId> IExprHierarchicalIdSP;
class IExprBitSlice;
using IExprBitSliceUP=UP<IExprBitSlice>;
typedef std::shared_ptr<IExprBitSlice> IExprBitSliceSP;
class IExprRefPathContext;
using IExprRefPathContextUP=UP<IExprRefPathContext>;
class IExprRefPathContext : public virtual IExprRefPath {
public:
    
    virtual ~IExprRefPathContext() { }
    
    
    virtual bool getIs_super() const = 0;
    
    virtual void setIs_super(bool v) = 0;
    
    virtual IExprHierarchicalId *getHier_id() const = 0;
    
    virtual void setHier_id(IExprHierarchicalId *v, bool own=true) = 0;
    
    virtual IExprBitSlice *getSlice() const = 0;
    
    virtual void setSlice(IExprBitSlice *v, bool own=true) = 0;
};
    
    } // namespace zsp
    } // namespace ast
    
