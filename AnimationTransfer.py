import math
import pymel.core as pm

def getRoot():
    selection = pm.selected()
    root = selection[0]  # First selection
    target_root = selection[1]  # Second selection
    return root, target_root

def getJoints(node, joint_list):
    for child in node.getChildren():
        joint_list.append(child)
        if child.numChildren() > 0:
            getJoints(child, joint_list)

def getParentRotation(node_name, matrix, list, ref_list):
    pm.currentTime(0, edit = True)
    node = pm.nodetypes.Joint(node_name)
    if node in ref_list:
        list.append(matrix)
    mat = node.getRotation().asMatrix()
    mat2 = node.getOrientation().asMatrix()
    mat3 = mat * mat2
    finalMat = mat3 * matrix
    children = node.getChildren()
    for child in children:
        getParentRotation(child, finalMat, list, ref_list)

def toEuler(mat):
    x = math.atan2(mat[1][2], mat[2][2])
    y = -math.asin(mat[0][2])
    z = math.atan2(mat[0][1], mat[0][0])
    return [math.degrees(x), math.degrees(y), math.degrees(z)]

def getJointList(root_name):
    list = []
    list.append(pm.nodetypes.Joint(root_name))
    getJoints(list[0], list)
    return list

def transfer(s_joint_list, t_joint_list):
    attrib_list = ["rotateX", "rotateY", "rotateZ", "scaleX", "scaleY", "scaleZ", "translateX", "translateY", "translateZ", "visibility"]  # Pre-defined list of keyable attributes
    i = 0
    
    s_parents = []
    t_parents = []
    
    getParentRotation(pm.nodetypes.Joint(s_joint_list[0]), pm.datatypes.Matrix(), s_parents, s_joint_list)
    getParentRotation(pm.nodetypes.Joint(t_joint_list[0]), pm.datatypes.Matrix(), t_parents, t_joint_list)
    
    while i < len(s_joint_list):
        print "Current joint: " + str(i)
        pm.currentTime(0, edit = True) #For getting bindposes
        currentSJoint = pm.nodetypes.Joint(s_joint_list[i])
        currentTJoint = pm.nodetypes.Joint(t_joint_list[i])
        s_bindpose = currentSJoint.getRotation().asMatrix() #Get bindpose for this source joint
        t_bindpose = currentTJoint.getRotation().asMatrix() #Get bindpose for this target joint
        if i == 0: #If it's the root joint
            for counter, attribute in enumerate(attrib_list):
                keyframes = pm.animation.keyframe(currentSJoint + "." + attribute, query = True) #Get all keyframes for the current attribute in joint
                for frame in keyframes:
                    if counter < 3: #If we're setting rotation data, calculate new basis
                        pm.currentTime(frame, edit = True)
                        
                        isolatedRotation = s_bindpose.inverse() * currentSJoint.getRotation().asMatrix()
                        worldSpaceRotation = currentSJoint.getOrientation().asMatrix().inverse() * isolatedRotation * currentSJoint.getOrientation().asMatrix()
                        translatedRotation = currentTJoint.getOrientation().asMatrix() * worldSpaceRotation * currentTJoint.getOrientation().asMatrix().inverse()
                        finalRotation = t_bindpose * translatedRotation
                        
                        value = toEuler(finalRotation)[counter]
                        pm.animation.setKeyframe(currentTJoint, at = attribute, time = frame, v = value)
                    else:
                        value = pm.animation.keyframe(currentSJoint, at = attribute, time = frame, eval = True, query = True)
                        print "Value: " + str(value) + " at attribute: " + attribute + " in joint: " + str(currentTJoint)
                        pm.animation.setKeyframe(currentTJoint, at = attribute, time = frame, v = value[0])
        else:
            for counter, attribute in enumerate(attrib_list):
                keyframes = pm.animation.keyframe(currentSJoint + "." + attribute, query = True)
                for frame in keyframes:
                    if counter < 3:
                        pm.currentTime(frame, edit = True)
                        
                        isolatedRotation = s_bindpose.inverse() * currentSJoint.getRotation().asMatrix()
                        worldSpaceRotation = s_parents[i].inverse() * currentSJoint.getOrientation().asMatrix().inverse() * isolatedRotation * currentSJoint.getOrientation().asMatrix() * s_parents[i]
                        translatedRotation = currentTJoint.getOrientation().asMatrix() * t_parents[i] * worldSpaceRotation * t_parents[i].inverse() * currentTJoint.getOrientation().asMatrix().inverse()
                        finalRotation = t_bindpose * translatedRotation
                        
                        value = toEuler(finalRotation)[counter]
                        print "Value: " + str(value) + " at attribute: " + attribute + " in joint: " + str(currentTJoint)
                        pm.animation.setKeyframe(currentTJoint, at = attribute, time = frame, v = value)
                    else:
                        pm.animation.setKeyframe(currentTJoint, at = attribute, time = frame) #If other attributes than rotation are keyed, put a key on these too but with the current value
        i += 1 #Go to next joint

def main():
    selection = pm.selected()
    root = selection[0]  # First selection
    target_root = selection[1]  # Second selection

    s_jnt_list = []  # List of source joints
    t_jnt_list = []  # List of target joints
    keys = []  # List of key times
    attr_list = ["rotateX", "rotateY", "rotateZ", "scaleX", "scaleY", "scaleZ", "translateX", "translateY", "translateZ", "visibility"]  # Pre-defined list of keyable attributes

    s_jnt_list.append(root) #Adds source root joint to source joint list
    t_jnt_list.append(target_root) #Adds target root joint to target joint list
    getJoints(root, s_jnt_list) #Attends children source joints to source joint list
    getJoints(target_root, t_jnt_list) #Appends children target joints to target joint list
    transfer(t_jnt_list, s_jnt_list, attr_list, keys)