/****************************************************************************
 * IField.h
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
#include "zsp/ast/INamedScopeChild.h"

#include "zsp/ast/FieldAttr.h"
namespace zsp {
namespace ast {

class INamedScopeChild;
using INamedScopeChildUP=UP<INamedScopeChild>;
typedef std::shared_ptr<INamedScopeChild> INamedScopeChildSP;
class IDataType;
using IDataTypeUP=UP<IDataType>;
typedef std::shared_ptr<IDataType> IDataTypeSP;
class IExpr;
using IExprUP=UP<IExpr>;
typedef std::shared_ptr<IExpr> IExprSP;
class IField;
using IFieldUP=UP<IField>;
class IField : public virtual INamedScopeChild {
public:
    
    virtual ~IField() { }
    
    
    virtual IDataType *getType() const = 0;
    
    virtual void setType(IDataType *v, bool own=true) = 0;
    
    virtual FieldAttr getAttr() const = 0;
    
    virtual void setAttr(FieldAttr v) = 0;
    
    virtual IExpr *getInit() const = 0;
    
    virtual void setInit(IExpr *v, bool own=true) = 0;
};
    
    } // namespace zsp
    } // namespace ast
    
