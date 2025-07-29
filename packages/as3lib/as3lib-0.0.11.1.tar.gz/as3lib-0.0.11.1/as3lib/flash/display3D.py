class Context3D:
   pass
class Context3DBlendFactor:
   pass
class Context3DBufferUsage:
   pass
class Context3DClearMask:
   pass
class Context3DCompareMode:
   pass
class Context3DFillMode:
   pass
class Context3DMipFilter:
   pass
class Context3DProfile:
   pass
class Context3DProgramType:
   pass
class Context3DRenderMode:
   pass
class Context3DStencilAction:
   pass
class Context3DTextureFilter:
   pass
class Context3DTextureFormat:
   pass
class Context3DTriangleFace:
   pass
class Context3DVertexBufferFormat:
   pass
class Context3DWrapModer:
   pass
class IndexBuffer3D:
   pass
class Program3D:
   pass
class textures:
   class CubeTexture:
      pass
   class RectagleTexture:
      pass
   class Texture(textures.TextureBase):
      def __init__():
         pass
      def uploadCompressedTextureFromByteArray(data, byteArrayOffset, async_):
         pass
      def uploadFromBitmapData(source, miplevel=0):
         pass
      def uploadFromBitmapDataAsync(source, miplevel=0):
         pass
      def uploadFromByteArray(data, byteArrayOffset, miplevel=0):
         pass
      def uploadFromByteArrayAsync(data, byteArrayOffset, miplevel=0):
         pass
   class TextureBase:
      def __init__(self):
         self.dimensions = [None,None] #width, height
         self.format_ = None
         self.data = None #byteArray
      def dispose():
         """
         Frees all GPU resources associated with this texture. After disposal, calling upload() or rendering with this object fails.
         """
         pass
   class VideoTexture:
      pass
class VertexBuffer3D:
   pass
