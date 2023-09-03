#    fchart3 draws beautiful deepsky charts in vector formats
#    Copyright (C) 2005-2023 fchart authors
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

from enum import Enum

class SpaceAllocatorType(Enum):
    BOTTOM = 1
    TOP = 2
    LEFT = 3
    RIGHT = 3


class SpaceHorizontalAllocator:
    def __init__(self, left, right, y, is_top):
        self.left, self.right = left, right
        self.is_top = is_top
        self.cur_left, self.cur_right = self.left, self.right
        self.y = y
        self.next_y = None

    def alloc_space(self, width, height, from_left):
        if self.cur_right - self.cur_left < width:
            if self.next_y is None:
                return None, None
            self.cur_left = self.left
            self.cur_right = self.right
            self.y = self.next_y
        if from_left:
            x = self.cur_left
            self.cur_left = self.cur_left + width
        else:
            self.cur_right = self.cur_right - width
            x = self.cur_right
        if self.is_top:
            y = self.y
            if self.next_y is None or self.y - height < self.next_y:
                self.next_y = self.y - height
        else:
            y = self.y + height
            if self.next_y is None or self.y + height > self.next_y:
                self.next_y = self.y + height
        return x, y

    def get_border_path(self):
        if self.next_y is None:
            result = [(self.left, self.y),(self.right, self.y)]
        else:
            result = []
            if self.cur_left != self.left:
                result.extend([(self.left, self.next_y), (self.cur_left, self.next_y), (self.cur_left, self.y)])
            else:
                result.append((self.left, self.y))
            if self.cur_right != self.right:
                result.extend([(self.cur_right, self.y), (self.cur_right, self.next_y), (self.right, self.next_y)])
            else:
                result.append((self.right, self.y))
        if self.is_top:
            result = result[::-1]
        return result

    def get_clip_y(self):
        return self.next_y if self.next_y is not None else self.y

class SpaceVerticalAllocator:
    def __init__(self, bottom, top, x, is_left):
        self.bottom, self.top = bottom, top
        self.is_left = is_left
        self.cur_bottom, self.cur_top = self.bottom, self.top
        self.x = x
        self.next_x = None

    def alloc_space(self, width, height, from_bottom):
        if self.cur_top - self.cur_bottom < height:
            if self.next_x is None:
                return None, None
            self.cur_bottom = self.bottom
            self.cur_top = self.top
            self.x = self.next_x

        if from_bottom:
            self.cur_bottom = self.cur_bottom + height
            y = self.cur_bottom
        else:
            y = self.cur_top
            self.cur_top = self.cur_top - height
        if self.is_left:
            x = self.x
            if self.next_x is None or self.x + width > self.next_x:
                self.next_x = self.x + width
        else:
            x = self.x - width
            if self.next_x is None or self.x - width < self.next_x:
                self.next_x = self.x - width
        return x, y

    def get_border_path(self):
        if self.next_x is None:
            result = [(self.x, self.top),(self.x, self.bottom)]
        else:
            result = []
            if self.cur_bottom != self.bottom:
                result.extend([(self.next_x, self.bottom), (self.next_x, self.cur_bottom), (self.x, self.cur_bottom)])
            else:
                result.append((self.x, self.bottom))
            if self.cur_top != self.top:
                result.extend([(self.x, self.cur_top), (self.next_x, self.cur_top), (self.next_x, self.top)])
            else:
                result.append((self.x, self.top))
        if self.is_left:
            result = result[::-1]
        return result

    def get_clip_x(self):
        return self.next_x if self.next_x is not None else self.x

class SpaceWidgetAllocator:
    def __init__(self, x1, y1, x2, y2):
        self.x1, self.y1, self.x2, self.y2 = x1, y1, x2, y2
        self.cur_allocator = None
        self.cur_allocator_type = None
        self.border_bottom = [(x1, y1), (x2, y1)]
        self.border_right = [(x2, y1), (x2, y2)]
        self.border_top = [(x2, y2), (x1, y2)]
        self.border_left = [(x1, y2), (x1, y1)]

    def alloc_space(self, width, height, alloc_spec):
        if not alloc_spec:
            return None
        als_items = alloc_spec.split(',')
        if len(als_items) == 2:
            allocator = None
            from_left_bottom = None
            if als_items[0] == 'left':
                allocator = self._get_allocator(SpaceAllocatorType.LEFT)
                from_left_bottom = (als_items[1] == 'bottom')
            if als_items[0] == 'right':
                allocator = self._get_allocator(SpaceAllocatorType.RIGHT)
                from_left_bottom = (als_items[1] == 'bottom')
            if als_items[0] == 'top':
                allocator = self._get_allocator(SpaceAllocatorType.TOP)
                from_left_bottom = (als_items[1] == 'left')
            if als_items[0] == 'bottom':
                allocator = self._get_allocator(SpaceAllocatorType.BOTTOM)
                from_left_bottom = (als_items[1] == 'left')
            if allocator is not None:
                return allocator.alloc_space(width, height, from_left_bottom)
        return None, None

    def get_border_path(self):
        self._actualize_borders()
        clip_path = self._join_borders(self.border_bottom, self.border_right)
        clip_path = self._join_borders(clip_path, self.border_top)
        clip_path = self._join_borders(clip_path, self.border_left)
        #print('{}'.format(clip_path), flush=True)
        for i in range(1, len(clip_path)):
            line1 = [(clip_path[i-1][0], clip_path[i-1][1]), (clip_path[i][0], clip_path[i][1])]
            for j in range(len(clip_path)-1, 0, -1):
                line2 = [(clip_path[j-1][0], clip_path[j-1][1]), (clip_path[j][0], clip_path[j][1])]
                itersect_point = self._intersect_lines(line1, line2)
                if itersect_point is not None:
                    clip_path = clip_path[i:j]
                    clip_path.append(itersect_point)
                    # print('1: {}'.format(clip_path), flush=True)
                    return clip_path
        # print('2: {}'.format(clip_path), flush=True)
        return clip_path

    def _get_allocator(self, allocator_type):
        if self.cur_allocator is None or self.cur_allocator_type != allocator_type:
            if self.cur_allocator_type is not None:
                self._actualize_borders()
                if self.cur_allocator_type == SpaceAllocatorType.BOTTOM:
                    self.y1 = self.cur_allocator.get_clip_y()
                elif self.cur_allocator_type == SpaceAllocatorType.TOP:
                    self.y2 = self.cur_allocator.get_clip_y()
                elif self.cur_allocator_type == SpaceAllocatorType.LEFT:
                    self.x1 = self.cur_allocator.get_clip_x()
                elif self.cur_allocator_type == SpaceAllocatorType.RIGHT:
                    self.x2 = self.cur_allocator.get_clip_x()

            if allocator_type == SpaceAllocatorType.BOTTOM:
                self.cur_allocator = SpaceHorizontalAllocator(self.x1, self.x2, self.y1, False)
            elif allocator_type == SpaceAllocatorType.TOP:
                self.cur_allocator = SpaceHorizontalAllocator(self.x1, self.x2, self.y2, True)
            elif allocator_type == SpaceAllocatorType.LEFT:
                self.cur_allocator = SpaceVerticalAllocator(self.y1, self.y2, self.x1, True)
            elif allocator_type == SpaceAllocatorType.RIGHT:
                self.cur_allocator = SpaceVerticalAllocator(self.y1, self.y2, self.x2, True)
            self.cur_allocator_type = allocator_type
        return self.cur_allocator

    def _intersect_lines(self, line1, line2):
        l1_x1, l1_y1, l1_x2, l1_y2 = line1[0][0], line1[0][1], line1[1][0], line1[1][1]
        l2_x1, l2_y1, l2_x2, l2_y2 = line2[0][0], line2[0][1], line2[1][0], line2[1][1]
        if l1_y1 == l1_y2:
            if l2_y1 == l2_y2:
                return None
            if l1_x1 > l1_x2:
                l1_x1, l1_x2 = l1_x2, l1_x1
            if l2_y1 > l2_y2:
                l2_y1, l2_y2 = l2_y2, l2_y1
            if l1_x1 <= l2_x1 and l1_x2 >= l2_x1 and l1_y1 >= l2_y1 and l1_y1 <= l2_y2:
                return (l2_x1, l1_y1)
        else:
            if l2_x1 == l2_x2:
                return None
            if l1_y1 > l1_y2:
                l1_y1, l1_y2 = l1_y2, l1_y1
            if l2_x1 > l2_x2:
                l2_x1, l2_x2 = l2_x2, l2_x1
            if l1_y1 <= l2_y1 and l1_y2 >= l2_y1 and l1_x1 >= l2_x1 and l1_x1 <= l2_x2:
                return (l1_x1, l2_y1)
        return None

    def _join_borders(self, border1, border2):
        # print('Join {} {}'.format(border1, border2))
        for i in range(len(border1)-1, 0, -1):
            line1 = [(border1[i-1][0], border1[i-1][1]), (border1[i][0], border1[i][1])]
            for j in range(1, len(border2)):
                line2 = [(border2[j-1][0], border2[j-1][1]), (border2[j][0], border2[j][1])]
                itersect_point = self._intersect_lines(line1, line2)
                if itersect_point is not None:
                    result = border1[:i]
                    result.append(itersect_point)
                    result.extend(border2[j:])
                    # print('Joined1 {}'.format(result))
                    return result
        result = border1[:]
        result.extend(border2)
        # print('Joined2 {}'.format(result))
        return result


    def _actualize_borders(self):
        if self.cur_allocator_type == SpaceAllocatorType.BOTTOM:
            self.border_bottom = self.cur_allocator.get_border_path()
        elif self.cur_allocator_type == SpaceAllocatorType.TOP:
            self.border_top = self.cur_allocator.get_border_path()
        elif self.cur_allocator_type == SpaceAllocatorType.LEFT:
            self.border_left = self.cur_allocator.get_border_path()
        elif self.cur_allocator_type == SpaceAllocatorType.RIGHT:
            self.border_right = self.cur_allocator.get_border_path()
