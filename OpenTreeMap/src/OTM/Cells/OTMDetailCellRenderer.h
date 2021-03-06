// This file is part of the OpenTreeMap code.
//
// OpenTreeMap is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// OpenTreeMap is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with OpenTreeMap.  If not, see <http://www.gnu.org/licenses/>.

#import <Foundation/Foundation.h>
#import "OTMDetailTableViewCell.h"
#import "OTMDBHTableViewCell.h"
#import "OTMBenefitsTableViewCell.h"

#define kOTMDefaultDetailRenderer OTMLabelDetailCellRenderer
#define kOTMDefaultEditDetailRenderer OTMLabelEditDetailCellRenderer

@class OTMEditDetailCellRenderer;
@class OTMUser;

/**
 * Generic interface for rendering cells
 * Note that the OTMEditDetailCellRender is responsible
 * for handling edit mode
 */
@interface OTMDetailCellRenderer : NSObject

/**
 * Use the given dict as the bases for the cell renderer
 */
+(OTMDetailCellRenderer *)cellRendererFromDict:(NSDictionary *)dict user:(OTMUser *)user;

/**
 * Key to access data for this cell
 *
 * Examples:
 *  tree.dbh (tree diameter)
 *  id       (plot id)
 */
@property (nonatomic,strong) NSString *dataKey;

/**
 * Key to access data for the second line of this cell.
 * Used primarily for showing the species scientific name
 * beneath the common name.
 *
 * Example:
 *  tree.scientific_name
 */
@property (nonatomic,strong) NSString *detailDataKey;

/**
 * Key to indicate that this field is linked to the
 * value of another field. Used primarily to link
 * the species scientific name field to the species
 * id.
 *
 * Example:
 *  tree.species
 */
@property (nonatomic,strong) NSString *ownerDataKey;

/**
 * Block that takes a single argument (the renderer)
 * and returns a UITableViewCell
 *
 * Default returns table cell with "default" cell styling
 */
@property (nonatomic,strong) Function1 newCellBlock;

/**
 * If this is <nil> then this cell is readonly
 * if this is non-nil the renderer returned will be used for editing
 */
@property (nonatomic,strong) OTMEditDetailCellRenderer *editCellRenderer;

// Table View Delegate methods
@property (nonatomic,strong) Function1v clickCallback;
@property (nonatomic,assign) CGFloat cellHeight;

/**
 * Initialize with dictionary structure
 */
-(id)initWithDict:(NSDictionary *)dict user:(OTMUser*)user;

/**
 * Given a tableView create a new cell (or reuse an old one), prepare
 * it with the given data and this cells rending info and return it
 */
ABSTRACT_METHOD
-(UITableViewCell *)prepareCell:(NSDictionary *)data inTable:(UITableView *)tableView;

@end


@interface OTMBenefitsDetailCellRenderer : OTMDetailCellRenderer

@property (nonatomic,strong) OTMBenefitsTableViewCell *cell;

@end

/**
 * Render cells for editing
 */
@interface OTMEditDetailCellRenderer : OTMDetailCellRenderer

+(OTMEditDetailCellRenderer *)editCellRendererFromDict:(NSDictionary *)dict user:(OTMUser *)user;

ABSTRACT_METHOD
-(NSDictionary *)updateDictWithValueFromCell:(NSDictionary *)dict;

@end

/**
 * Render a simple label
 */
@interface OTMLabelDetailCellRenderer : OTMDetailCellRenderer

@property (nonatomic,strong) NSString *label;
@property (nonatomic,strong) NSString *formatStr;

@end

@interface OTMLabelEditDetailCellRenderer : OTMEditDetailCellRenderer<OTMDetailTableViewCellDelegate>

@property (nonatomic,assign) UIKeyboardType keyboard;
@property (nonatomic,strong) NSString *label;
@property (nonatomic,strong) NSString *updatedString;

-(UIKeyboardType)decodeKeyboard:(NSString *)ktype;

@end

@interface OTMDBHEditDetailCellRenderer : OTMEditDetailCellRenderer<OTMDetailTableViewCellDelegate>

@property (nonatomic,strong) OTMDBHTableViewCell *cell;

@end

/**
 * Shows a static cell that allows a click event
 * (Such as for selecting species)
 *
 * When the user clicks on the cell "callback"
 * is invoked. When editing is finished the value
 * (if non-nil) from data is used as the edited value
 */
@interface OTMStaticClickCellRenderer : OTMEditDetailCellRenderer

-(id)initWithName:(NSString *)aName key:(NSString *)key clickCallback:(Function1v)aCallback;

-(id)initWithKey:(NSString *)key clickCallback:(Function1v)aCallback;

@property (nonatomic,strong) NSString *defaultName;
@property (nonatomic,strong) NSString *name;
@property (nonatomic,strong) id data;

@end
